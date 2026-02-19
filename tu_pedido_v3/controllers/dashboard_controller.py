from odoo import http, fields
from odoo.http import request
from datetime import timedelta
import json

class DashboardController(http.Controller):
    
    @http.route('/tu_pedido_v3/dashboard', type='http', auth='user', website=True)
    def dashboard(self, **kwargs):
        return request.render('tu_pedido_v3.dashboard_template', {})
    
    @http.route('/tu_pedido_v3/dashboard_data', type='json', auth='user')
    def dashboard_data(self):
        estados = [
            {'key': 'nuevo', 'title': '🆕 Nuevo'},
            {'key': 'aceptado', 'title': '✅ Aceptado'},
            {'key': 'en_preparacion', 'title': '👨‍🍳 En Preparación'},
            {'key': 'terminado', 'title': '✔️ Terminado'},
            {'key': 'despachado', 'title': '🚚 Despachado'},
            {'key': 'entregado', 'title': '📦 Entregado'},
            {'key': 'rechazado', 'title': '❌ Rechazado'}
        ]
        
        columns = []
        for estado in estados:
            orders = request.env['sale.order'].search([
                ('estado_rapido', '=', estado['key'])
            ], order='create_date desc')
            
            orders_data = []
            for order in orders:
                orders_data.append({
                    'id': order.id,
                    'name': order.name,
                    'partner_id': [order.partner_id.id, order.partner_id.name],
                    'productos': self._get_productos(order),
                    'nota_cocina': order.nota_cocina or '',
                    'tiempo_estado': order.tiempo_estado_minutos,
                    'tiempo_total': order.tiempo_total_minutos,
                    'sonido_activo': order.sonido_activo,
                    'es_para_envio': order.es_para_envio,
                    'direccion_entrega_completa': order.direccion_entrega_completa or '',
                    'estado_rapido': order.estado_rapido,
                    'tiene_reclamo': order.tiene_reclamo,
                    'descripcion_reclamo': order.descripcion_reclamo or '',
                    'productos_modificados': order.productos_modificados,
                    'detalles_cambios': order.detalles_cambios or '',
                    'tipo_pedido': 'web' if order.website_id else 'pos',
                    'create_date': order.create_date.isoformat() if order.create_date else None,
                })
            
            columns.append({
                'key': estado['key'],
                'title': estado['title'],
                'orders': orders_data,
                'count': len(orders_data)
            })
        
        return {'columns': columns}
    
    def _get_productos(self, order):
        productos = []
        for line in order.order_line:
            # Obtener atributos del producto
            attributes = []
            if line.product_template_attribute_value_ids:
                for attr_value in line.product_template_attribute_value_ids:
                    attributes.append({
                        'attribute': attr_value.attribute_id.name,
                        'value': attr_value.name
                    })
            
            productos.append({
                'id': line.id,
                'name': line.product_id.name,
                'qty': line.product_uom_qty,
                'uom': line.product_uom_id.name if line.product_uom_id else 'Unidad',
                'completado': False,
                'attributes': attributes
            })
        return productos
    
    @http.route('/tu_pedido_v3/cambiar_estado', type='json', auth='user')
    def cambiar_estado(self, order_id, nuevo_estado):
        order = request.env['sale.order'].browse(order_id)
        if order.exists():
            order.action_cambiar_estado(nuevo_estado)
            return {'success': True}
        return {'success': False}
    
    @http.route('/tu_pedido_v3/siguiente_estado', type='json', auth='user')
    def siguiente_estado(self, order_id):
        order = request.env['sale.order'].browse(order_id)
        if order.exists():
            order.action_siguiente_estado()
            return {'success': True}
        return {'success': False}
    
    @http.route('/tu_pedido_v3/aceptar_pedido', type='json', auth='user')
    def aceptar_pedido(self, order_id):
        order = request.env['sale.order'].browse(order_id)
        if order.exists():
            order.action_cambiar_estado('aceptado')
            return {'success': True}
        return {'success': False}
    
    @http.route('/tu_pedido_v3/rechazar_pedido', type='json', auth='user')
    def rechazar_pedido(self, order_id, motivo=''):
        order = request.env['sale.order'].browse(order_id)
        if order.exists():
            order.write({'nota_cocina': f"{order.nota_cocina or ''}\nMotivo rechazo: {motivo}"})
            order.action_cambiar_estado('rechazado')
            return {'success': True}
        return {'success': False}
    
    @http.route('/tu_pedido_v3/toggle_producto', type='json', auth='user')
    def toggle_producto(self, order_id, line_id):
        return {'success': True}
    
    @http.route('/tu_pedido_v3/get_detalles_cambios', type='json', auth='user')
    def get_detalles_cambios(self, order_id):
        """Obtener detalles de cambios de productos"""
        try:
            order = request.env['sale.order'].browse(order_id)
            if order.exists() and order.detalles_cambios:
                import ast
                detalles = ast.literal_eval(order.detalles_cambios)
                return {'success': True, 'detalles': detalles}
            return {'success': False, 'detalles': {'agregados': [], 'modificados': [], 'eliminados': []}}
        except Exception as e:
            return {'success': False, 'detalles': {'agregados': [], 'modificados': [], 'eliminados': []}}
    
    @http.route('/tu_pedido_v3/aceptar_cambios_productos', type='json', auth='user')
    def aceptar_cambios_productos(self, order_id, motivo=''):
        """Aceptar cambios en productos"""
        order = request.env['sale.order'].browse(order_id)
        if order.exists():
            order.write({'productos_modificados': False, 'detalles_cambios': False})
            return {'success': True}
        return {'success': False}
    
    @http.route('/tu_pedido_v3/rechazar_cambios_productos', type='json', auth='user')
    def rechazar_cambios_productos(self, order_id, motivo=''):
        """Rechazar cambios en productos"""
        order = request.env['sale.order'].browse(order_id)
        if order.exists():
            order.write({
                'productos_modificados': False,
                'detalles_cambios': False,
                'estado_rapido': 'rechazado',
                'motivo_rechazo': f"Cambios rechazados: {motivo}"
            })
            return {'success': True}
        return {'success': False}
