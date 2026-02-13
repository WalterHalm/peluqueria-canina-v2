# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Visita(models.Model):
    _name = 'peluqueria.visita'
    _description = 'Visitas/Atenciones de Peluquería'
    _order = 'fecha desc'
    _rec_name = 'display_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    display_name = fields.Char(string='Visita', compute='_compute_display_name', store=True)
    name = fields.Char(string='Número', required=True, copy=False, readonly=True, default=lambda self: _('Nuevo'))
    mascota_id = fields.Many2one('peluqueria.mascota', string='Mascota', required=True, tracking=True, ondelete='restrict')
    cliente_id = fields.Many2one('res.partner', string='Cliente', related='mascota_id.owner_id', store=True, readonly=True)
    fecha = fields.Datetime(string='Fecha y Hora', required=True, default=fields.Datetime.now, tracking=True)
    turno_id = fields.Many2one('peluqueria.turno', string='Turno Origen', readonly=True)
    
    servicio_ids = fields.Many2many('peluqueria.servicio', 'visita_servicio_rel', 'visita_id', 'servicio_id', string='Servicios Realizados', required=True)
    producto_line_ids = fields.One2many('peluqueria.visita.producto', 'visita_id', string='Productos Utilizados')
    empleado_id = fields.Many2one('res.users', string='Peluquero', tracking=True)
    
    # Centro de Costos
    precio_servicios = fields.Monetary(string='Precio Servicios', compute='_compute_totales', store=True, currency_field='currency_id')
    costo_productos = fields.Monetary(string='Costo Productos', compute='_compute_totales', store=True, currency_field='currency_id')
    otros_gastos = fields.Monetary(string='Otros Gastos', currency_field='currency_id')
    costo_total = fields.Monetary(string='Costo Total', compute='_compute_totales', store=True, currency_field='currency_id')
    total_venta = fields.Monetary(string='Total Venta', compute='_compute_totales', store=True, currency_field='currency_id')
    ganancia = fields.Monetary(string='Ganancia', compute='_compute_totales', store=True, currency_field='currency_id')
    margen_porcentaje = fields.Float(string='Margen (%)', compute='_compute_totales', store=True)
    currency_id = fields.Many2one('res.currency', string='Moneda', default=lambda self: self.env.company.currency_id)
    
    state = fields.Selection([('nuevo', 'Nuevo'), ('en_proceso', 'En Proceso'), ('terminado', 'Terminado'), ('no_asistio', 'No Asistió')], string='Estado', default='nuevo', required=True, tracking=True, copy=False)
    factura_id = fields.Many2one('account.move', string='Factura', readonly=True, copy=False)
    facturado = fields.Boolean(string='Facturado', compute='_compute_facturado', store=True)
    
    notas = fields.Text(string='Observaciones')
    notas_internas = fields.Text(string='Notas Internas')
    imagen_antes = fields.Image(string='Foto Antes', max_width=1024, max_height=1024, attachment=True)
    imagen_despues = fields.Image(string='Foto Después', max_width=1024, max_height=1024, attachment=True)
    color = fields.Integer(string='Color', compute='_compute_color')
    
    @api.depends('mascota_id', 'fecha')
    def _compute_display_name(self):
        for record in self:
            if record.mascota_id and record.fecha:
                fecha_str = fields.Datetime.context_timestamp(record, record.fecha).strftime('%d/%m/%Y')
                record.display_name = f"{record.mascota_id.name} - {fecha_str}"
            else:
                record.display_name = record.name or "Nueva Visita"
    
    @api.depends('servicio_ids', 'producto_line_ids', 'otros_gastos')
    def _compute_totales(self):
        for record in self:
            record.precio_servicios = sum(record.servicio_ids.mapped('precio'))
            record.costo_productos = sum(record.producto_line_ids.mapped('subtotal_costo'))
            record.costo_total = record.costo_productos + record.otros_gastos
            record.total_venta = record.precio_servicios
            record.ganancia = record.total_venta - record.costo_total
            record.margen_porcentaje = (record.ganancia / record.total_venta * 100) if record.total_venta else 0.0
    
    @api.depends('factura_id')
    def _compute_facturado(self):
        for record in self:
            record.facturado = bool(record.factura_id)
    
    @api.depends('state')
    def _compute_color(self):
        color_map = {
            'nuevo': 7,         # Gris
            'en_proceso': 2,    # Naranja
            'terminado': 4,     # Azul
            'no_asistio': 1,    # Rojo
        }
        for record in self:
            record.color = color_map.get(record.state, 0)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == 'Nuevo':
                vals['name'] = self.env['ir.sequence'].next_by_code('peluqueria.visita') or 'Nuevo'
        return super().create(vals_list)
    
    def action_iniciar(self):
        self.write({'state': 'en_proceso'})
        return True
    
    def action_terminar(self):
        self.write({'state': 'terminado'})
        # Actualizar turno a asistio
        if self.turno_id and self.turno_id.state == 'confirmado':
            self.turno_id.write({'state': 'asistio'})
        return True
    
    def action_no_asistio(self):
        self.write({'state': 'no_asistio'})
        if self.turno_id:
            self.turno_id.write({'state': 'no_asistio'})
        return True
    
    def action_generar_factura(self):
        self.ensure_one()
        if self.factura_id:
            raise ValidationError("Esta visita ya tiene una factura generada")
        if not self.cliente_id:
            raise ValidationError('Debe seleccionar un cliente antes de generar la factura.')
        if not self.servicio_ids:
            raise ValidationError('Debe agregar al menos un servicio antes de generar la factura.')
        if self.state != 'confirmado':
            raise ValidationError('La visita debe estar confirmada para generar factura.')
        factura = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.cliente_id.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {'name': s.name, 'quantity': 1, 'price_unit': s.precio}) for s in self.servicio_ids],
        })
        self.write({'factura_id': factura.id, 'state': 'facturado'})
        return {'type': 'ir.actions.act_window', 'res_model': 'account.move', 'res_id': factura.id, 'view_mode': 'form', 'target': 'current'}
    
    def action_ver_factura(self):
        self.ensure_one()
        if not self.factura_id:
            raise ValidationError("Esta visita no tiene factura generada")
        return {'type': 'ir.actions.act_window', 'res_model': 'account.move', 'res_id': self.factura_id.id, 'view_mode': 'form', 'target': 'current'}
    
    def action_cancelar(self):
        if self.factura_id and self.factura_id.state == 'posted':
            raise ValidationError("No se puede cancelar una visita con factura confirmada")
        self.write({'state': 'cancelado'})
        return True


class VisitaProducto(models.Model):
    _name = 'peluqueria.visita.producto'
    _description = 'Productos Utilizados por Visita'
    
    visita_id = fields.Many2one('peluqueria.visita', string='Visita', required=True, ondelete='cascade')
    producto_id = fields.Many2one('product.product', string='Producto', required=True)
    cantidad = fields.Float(string='Cantidad', default=1.0, required=True)
    uom_id = fields.Many2one('uom.uom', string='Unidad', required=True)
    costo_unitario = fields.Float(string='Costo Unitario', compute='_compute_costo_unitario', store=True, readonly=False)
    subtotal_costo = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)
    currency_id = fields.Many2one('res.currency', related='visita_id.currency_id')
    
    @api.onchange('producto_id')
    def _onchange_producto_id(self):
        if self.producto_id:
            self.uom_id = self.producto_id.uom_id
            self.costo_unitario = self.producto_id.standard_price
    
    @api.depends('producto_id')
    def _compute_costo_unitario(self):
        for record in self:
            if record.producto_id and not record.costo_unitario:
                record.costo_unitario = record.producto_id.standard_price
    
    @api.depends('cantidad', 'costo_unitario', 'uom_id', 'producto_id')
    def _compute_subtotal(self):
        for record in self:
            if record.producto_id and record.uom_id:
                if record.uom_id != record.producto_id.uom_id:
                    cantidad_base = record.uom_id._compute_quantity(
                        record.cantidad,
                        record.producto_id.uom_id,
                        rounding_method='HALF-UP'
                    )
                else:
                    cantidad_base = record.cantidad
                    
                record.subtotal_costo = cantidad_base * record.costo_unitario
            else:
                record.subtotal_costo = record.cantidad * record.costo_unitario
