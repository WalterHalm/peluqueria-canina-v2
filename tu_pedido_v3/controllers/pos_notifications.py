from odoo import http
from odoo.http import request
import json

class PosNotificationsController(http.Controller):
    
    def _format_table_name(self, name):
        """Formatear nombre de mesa para separar piso y número"""
        if not name:
            return name
        
        import re
        # Buscar patrón: letras + "Mesa" + números
        match = re.match(r'^([A-Za-z]+)(Mesa)(\d+)$', name)
        if match:
            floor = match.group(1)
            table_num = match.group(3)
            return f"{floor} Mesa {table_num}"
        
        return name

    @http.route('/tu_pedido_v3/pos_delivery_notifications', type='json', auth='user')
    def get_pos_delivery_notifications(self):
        """Obtener notificaciones de delivery para el PoS"""
        notifications = []
        
        sale_delivery_orders = request.env['sale.order'].sudo().search([
            ('es_para_envio', '=', True),
            ('estado_rapido', '=', 'terminado')
        ])
        
        for order in sale_delivery_orders:
            tipo = 'web' if order.website_id else 'pos'
            order_name = self._format_table_name(order.name)
            
            notifications.append({
                'id': f'sale_{order.id}',
                'order_name': order_name,
                'cliente': order.partner_id.name,
                'direccion': order.direccion_entrega_completa or 'Sin dirección',
                'telefono': order.partner_id.phone or 'Sin teléfono',
                'tipo': tipo
            })
        
        return {'notifications': notifications}
    
    @http.route('/tu_pedido_v3/pos_pickup_notifications', type='json', auth='user')
    def get_pos_pickup_notifications(self):
        """Obtener notificaciones de pedidos listos para retirar"""
        notifications = []
        
        sale_pickup_orders = request.env['sale.order'].sudo().search([
            ('es_para_envio', '=', False),
            ('estado_rapido', '=', 'terminado')
        ])
        
        for order in sale_pickup_orders:
            tipo = 'web' if order.website_id else 'pos'
            order_name = self._format_table_name(order.name)
            
            notifications.append({
                'id': f'sale_{order.id}',
                'order_name': order_name,
                'cliente': order.partner_id.name,
                'telefono': order.partner_id.phone or 'Sin teléfono',
                'tipo': tipo
            })
        
        return {'notifications': notifications}
    
    @http.route('/tu_pedido_v3/pos_web_notifications', type='json', auth='user')
    def get_pos_web_notifications(self):
        """Obtener notificaciones de pedidos web nuevos para el PoS"""
        notifications = []
        
        # Buscar pedidos web en estado nuevo
        web_orders = request.env['sale.order'].sudo().search([
            ('website_id', '!=', False),
            ('estado_rapido', '=', 'nuevo')
        ])
        
        for order in web_orders:
            # Preparar productos
            productos_resumen = []
            for line in order.order_line[:3]:
                productos_resumen.append(f"{line.product_uom_qty}x {line.name}")
            
            productos_text = ', '.join(productos_resumen)
            if len(order.order_line) > 3:
                productos_text += f" y {len(order.order_line) - 3} más"
            
            notifications.append({
                'id': order.id,
                'order_name': order.name,
                'cliente': order.partner_id.name,
                'telefono': order.partner_id.phone or 'Sin teléfono',
                'direccion': order.direccion_entrega_completa or 'Retiro en local',
                'es_para_envio': order.es_para_envio,
                'productos': productos_text,
                'amount_total': order.amount_total,
                'create_date': order.create_date.isoformat()
            })
            
            # Marcar como visto para evitar duplicados en la primera carga
            if order.sonido_activo:
                order.sonido_activo = False
        
        return {'notifications': notifications}

    @http.route('/tu_pedido_v3/mark_delivery_dispatched', type='json', auth='user')
    def mark_delivery_dispatched(self):
        """Marcar pedido delivery como despachado"""
        try:
            data = request.get_json_data()
            order_id = data.get('order_id') if data else None
            
            if not order_id:
                return {'success': False, 'message': 'order_id requerido'}
            
            # Determinar si es PoS o Sale order
            if str(order_id).startswith('pos_'):
                real_id = int(order_id.replace('pos_', ''))
                order = request.env['pos.order'].sudo().browse(real_id)
                if order.exists():
                    order.action_cambiar_estado('despachado')
                    return {'success': True}
            elif str(order_id).startswith('sale_'):
                real_id = int(order_id.replace('sale_', ''))
                order = request.env['sale.order'].sudo().browse(real_id)
                if order.exists():
                    order.action_cambiar_estado('despachado')
                    return {'success': True}
            
            return {'success': False, 'message': 'Pedido no encontrado'}
        except Exception as e:
            return {'success': False, 'message': str(e)}