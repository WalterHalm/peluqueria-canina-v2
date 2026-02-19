from odoo import http, fields
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class EcommerceController(http.Controller):

    @http.route('/tu_pedido_v3/estado_restaurante', type='json', auth='public')
    def estado_restaurante(self):
        try:
            return {
                'success': True,
                'abierto': True,
                'fecha_apertura': fields.Datetime.now().isoformat(),
                'hora_cierre_estimada': 22.0,
                'mensaje': 'Restaurante abierto'
            }
        except Exception as e:
            return {'success': False, 'error': str(e), 'abierto': True}

    @http.route('/tu_pedido_v3/estado_pedido/<int:order_id>', type='json', auth='public')
    def estado_pedido(self, order_id):
        try:
            order = request.env['sale.order'].sudo().browse(order_id)
            if not order.exists():
                return {'success': False, 'error': 'Pedido no encontrado'}
            
            estados_cliente = {
                'nuevo': {'nombre': 'Recibido', 'progreso': 10, 'descripcion': 'Tu pedido ha sido recibido'},
                'aceptado': {'nombre': 'Confirmado', 'progreso': 25, 'descripcion': 'Tu pedido ha sido confirmado'},
                'preparacion': {'nombre': 'En Preparación', 'progreso': 50, 'descripcion': 'Estamos preparando tu pedido'},
                'terminado': {'nombre': 'Listo', 'progreso': 75, 'descripcion': 'Tu pedido está listo'},
                'despachado': {'nombre': 'Despachado', 'progreso': 90, 'descripcion': 'Tu pedido ha sido despachado'},
                'entregado': {'nombre': 'Entregado', 'progreso': 100, 'descripcion': 'Pedido entregado exitosamente'},
                'rechazado': {'nombre': 'Rechazado', 'progreso': 0, 'descripcion': 'Lo sentimos, tu pedido fue rechazado'}
            }
            
            estado_actual = estados_cliente.get(order.estado_rapido, {
                'nombre': 'Desconocido', 'progreso': 0, 'descripcion': 'Estado desconocido'
            })
            
            return {
                'success': True,
                'pedido': {
                    'id': order.id,
                    'nombre': order.name,
                    'cliente': order.partner_id.name,
                    'estado_codigo': order.estado_rapido,
                    'estado': estado_actual,
                    'tiempo_transcurrido': order.tiempo_total_minutos,
                    'puede_confirmar_recepcion': order.estado_rapido == 'despachado' and not order.cliente_confirmo_recepcion,
                    'productos': [{
                        'nombre': line.product_id.name,
                        'cantidad': line.product_uom_qty,
                        'precio': line.price_unit
                    } for line in order.order_line]
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @http.route('/tu_pedido_v3/confirmar_recepcion/<int:order_id>', type='json', auth='public')
    def confirmar_recepcion(self, order_id):
        try:
            order = request.env['sale.order'].sudo().browse(order_id)
            if not order.exists():
                return {'success': False, 'error': 'Pedido no encontrado'}
            
            if order.estado_rapido != 'despachado':
                return {'success': False, 'error': 'El pedido no está en estado despachado'}
            
            order.action_confirmar_recepcion_cliente()
            return {'success': True, 'mensaje': 'Recepción confirmada exitosamente'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @http.route('/tu_pedido_v3/generar_reclamo/<int:order_id>', type='json', auth='public')
    def generar_reclamo(self, order_id, **kwargs):
        try:
            motivo = kwargs.get('motivo', '')
            order = request.env['sale.order'].sudo().browse(order_id)
            if not order.exists():
                return {'success': False, 'error': 'Pedido no encontrado'}
            
            order.write({'tiene_reclamo': True, 'descripcion_reclamo': motivo})
            return {'success': True, 'mensaje': 'Reclamo generado exitosamente'}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class WebsiteSaleInherit(WebsiteSale):
    
    @http.route(['/shop/confirmation'], type='http', auth="public", website=True, sitemap=False)
    def shop_payment_confirmation(self, **post):
        response = super(WebsiteSaleInherit, self).shop_payment_confirmation(**post)
        
        if hasattr(response, 'qcontext'):
            order = response.qcontext.get('order')
            if order and order.estado_rapido:
                response.qcontext['show_tracking_button'] = True
        
        return response
