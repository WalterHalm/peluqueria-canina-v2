import json

from odoo import http, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleRaffle(WebsiteSale):
    """Extensión del controller de tienda para inyectar datos de sorteo
    en la página de detalle del producto ticket."""

    def _prepare_product_values(self, product, category, **kwargs):
        """Agrega datos del sorteo y tickets al contexto de la página de producto."""
        values = super()._prepare_product_values(product, category, **kwargs)
        raffle = product.raffle_id
        if raffle and product.is_raffle_ticket:
            tickets = raffle.ticket_ids.sudo().sorted('number')
            values['raffle'] = raffle.sudo()
            values['raffle_tickets'] = tickets
            values['raffle_tickets_json'] = json.dumps([{
                'id': t.id,
                'number': t.number,
                'name': t.name,
                'state': t.state,
                'buyer': t.partner_id.display_nickname if t.partner_id else '',
            } for t in tickets])
        return values


class RaffleTicketController(http.Controller):
    """Controller separado para las rutas JSON de tickets de rifa.
    No hereda de WebsiteSale para evitar interferir con el checkout."""

    @http.route('/shop/raffle/add_ticket', type='json', auth='public', website=True)
    def raffle_add_ticket_to_cart(self, ticket_id, **kwargs):
        """Agrega un ticket específico al carrito de compras.
        Se llama desde la cuadrícula cuando el cliente confirma la selección."""
        ticket = request.env['raffle.ticket'].sudo().browse(int(ticket_id))
        if not ticket.exists() or ticket.state != 'available':
            return {'error': _('Este ticket ya no está disponible.')}

        raffle = ticket.raffle_id
        product = raffle.ticket_product_id
        if not product:
            return {'error': _('Producto de ticket no encontrado.')}

        sale_order = request.cart or request.website._create_cart()

        # Verificar que no tenga ya este ticket en el carrito
        existing_line = sale_order.order_line.filtered(
            lambda l: l.raffle_ticket_id.id == ticket.id
        )
        if existing_line:
            return {'error': _('Este ticket ya está en tu carrito.')}

        # Agregar al carrito
        order_line = sale_order._cart_add(
            product_id=product.id,
            quantity=1,
        )
        # Vincular el ticket a la línea de venta (el nombre se recomputa automáticamente)
        if order_line and order_line.get('line_id'):
            line = request.env['sale.order.line'].sudo().browse(order_line['line_id'])
            line.raffle_ticket_id = ticket.id

        return {
            'success': True,
            'ticket_number': ticket.number,
            'cart_quantity': sale_order.cart_quantity,
        }
