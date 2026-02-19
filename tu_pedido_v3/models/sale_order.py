from odoo import models, fields, api
from datetime import datetime, timedelta
import json

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    estado_rapido = fields.Selection([
        ('nuevo', 'Nuevo'),
        ('aceptado', 'Aceptado'),
        ('preparacion', 'En Preparación'),
        ('terminado', 'Terminado'),
        ('despachado', 'Despachado/Retirado'),
        ('entregado', 'Entregado'),
        ('rechazado', 'Rechazado')
    ], string='Estado Rápido', default=False)
    
    nota_cocina = fields.Text(string='Notas de Cocina')
    tiempo_inicio_estado = fields.Datetime(string='Inicio Estado Actual')
    tiempo_inicio_total = fields.Datetime(string='Inicio Total')
    sonido_activo = fields.Boolean(string='Sonido Activo', default=False)
    es_para_envio = fields.Boolean(string='Es para Envío', default=False)
    direccion_entrega_completa = fields.Text(string='Dirección Completa')
    cliente_confirmo_recepcion = fields.Boolean(string='Cliente Confirmó Recepción', default=False)
    tiempo_estimado_entrega = fields.Integer(string='Tiempo Estimado (min)', default=30)
    tiene_reclamo = fields.Boolean(string='Tiene Reclamo', default=False)
    descripcion_reclamo = fields.Text(string='Descripción del Reclamo')
    productos_modificados = fields.Boolean(string='Productos Modificados', default=False)
    motivo_rechazo = fields.Text(string='Motivo del Rechazo')
    pos_reference = fields.Char(string='Referencia PoS', index=True)
    detalles_cambios = fields.Text(string='Detalles de Cambios')
    productos_snapshot = fields.Text(string='Snapshot de Productos')
    
    tiempo_estado_minutos = fields.Integer(string='Minutos en Estado', compute='_compute_tiempos')
    tiempo_total_minutos = fields.Integer(string='Minutos Totales', compute='_compute_tiempos')
    
    @api.depends('tiempo_inicio_estado', 'tiempo_inicio_total')
    def _compute_tiempos(self):
        for record in self:
            now = fields.Datetime.now()
            if record.tiempo_inicio_estado:
                delta = now - record.tiempo_inicio_estado
                record.tiempo_estado_minutos = int(delta.total_seconds() / 60)
            else:
                record.tiempo_estado_minutos = 0
            
            if record.tiempo_inicio_total:
                delta = now - record.tiempo_inicio_total
                record.tiempo_total_minutos = int(delta.total_seconds() / 60)
            else:
                record.tiempo_total_minutos = 0
    
    def action_confirm(self):
        result = super().action_confirm()
        
        for order in self:
            if order.website_id and not order.estado_rapido:
                is_cash_or_onsite = False
                for tx in order.transaction_ids:
                    if tx.provider_id.custom_mode in ['cash_on_delivery', 'on_site']:
                        is_cash_or_onsite = True
                        break
                
                if is_cash_or_onsite:
                    order.write({
                        'estado_rapido': 'nuevo',
                        'tiempo_inicio_estado': fields.Datetime.now(),
                        'tiempo_inicio_total': fields.Datetime.now(),
                        'sonido_activo': True,
                    })
                    order._detectar_tipo_entrega()
        
        return result
    
    def _detectar_tipo_entrega(self):
        self.ensure_one()
        
        tiene_envio = False
        tiene_recoleccion = False
        
        if self.carrier_id:
            if self.carrier_id.delivery_type == 'in_store':
                tiene_recoleccion = True
            elif self.carrier_id.delivery_type in ['fixed', 'base_on_rule']:
                tiene_envio = True
        
        for line in self.order_line:
            product_name = line.product_id.name.lower()
            if any(keyword in product_name for keyword in ['envío', 'envio', 'delivery', 'shipping', 'entrega']):
                tiene_envio = True
            if any(keyword in product_name for keyword in ['recolección', 'recoleccion', 'retiro', 'pickup']):
                tiene_recoleccion = True
        
        self.es_para_envio = tiene_envio and not tiene_recoleccion
        
        if self.es_para_envio:
            partner = self.partner_shipping_id or self.partner_id
            if partner:
                parts = []
                if partner.street:
                    parts.append(partner.street)
                if partner.street2:
                    parts.append(partner.street2)
                if partner.city:
                    parts.append(partner.city)
                if partner.state_id:
                    parts.append(partner.state_id.name)
                if partner.zip:
                    parts.append(partner.zip)
                self.direccion_entrega_completa = ', '.join(parts)
        else:
            self.direccion_entrega_completa = ''
    
    def action_cambiar_estado(self, nuevo_estado):
        self.ensure_one()
        if self.estado_rapido != nuevo_estado:
            vals = {
                'estado_rapido': nuevo_estado,
                'tiempo_inicio_estado': fields.Datetime.now()
            }
            if self.estado_rapido == 'nuevo' and nuevo_estado != 'nuevo':
                vals['sonido_activo'] = False
            
            if nuevo_estado == 'aceptado':
                self._crear_snapshot_productos()
                self.productos_modificados = False
            
            if nuevo_estado == 'terminado' and self.state == 'draft':
                self.action_confirm()
            elif nuevo_estado == 'rechazado':
                self.action_cancel()
            
            self.write(vals)
        return True
    
    def action_siguiente_estado(self):
        estados = ['nuevo', 'aceptado', 'preparacion', 'terminado', 'despachado', 'entregado']
        if self.estado_rapido in estados:
            idx = estados.index(self.estado_rapido)
            if idx < len(estados) - 1:
                self.action_cambiar_estado(estados[idx + 1])
        return True
    
    def action_confirmar_recepcion_cliente(self):
        self.write({
            'cliente_confirmo_recepcion': True,
            'estado_rapido': 'entregado'
        })
        return True
    
    def _crear_snapshot_productos(self):
        self.ensure_one()
        productos_info = []
        for line in self.order_line:
            productos_info.append({
                'product_id': line.product_id.id,
                'name': line.name,
                'product_uom_qty': line.product_uom_qty,
                'price_unit': line.price_unit
            })
        self.productos_snapshot = json.dumps(productos_info)
