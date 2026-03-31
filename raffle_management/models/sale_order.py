import random

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    """Herencia de sale.order.line para vincular la venta con un ticket de sorteo.
    Cuando se confirma una orden que contiene un producto ticket de rifa,
    se asigna el ticket al comprador y se acumula la semilla aleatoria."""
    _inherit = 'sale.order.line'

    raffle_ticket_id = fields.Many2one(
        'raffle.ticket',
        string='Ticket de Rifa',
        copy=False,
    )

    @api.depends('raffle_ticket_id')
    def _compute_name(self):
        """Extiende el compute del nombre para que se recompute
        cuando se asigna un ticket de rifa."""
        super()._compute_name()

    def _get_sale_order_line_multiline_description_sale(self):
        """Agrega el número de ticket a la descripción de la línea de venta.
        Ejemplo: 'Ticket - TV Samsung (#42)'"""
        description = super()._get_sale_order_line_multiline_description_sale()
        if self.raffle_ticket_id:
            description += '\n🎟️ Ticket #%s' % self.raffle_ticket_id.number
        return description

    def _action_launch_stock_rule(self, *, previous_product_uom_qty=False):
        """Al confirmar la orden de venta, si la línea tiene un ticket de rifa
        asignado, se marca como vendido y se acumula la semilla."""
        res = super()._action_launch_stock_rule(previous_product_uom_qty=previous_product_uom_qty)
        for line in self.filtered(lambda l: l.raffle_ticket_id and l.raffle_ticket_id.state == 'available'):
            line._sell_raffle_ticket()
        return res

    def _sell_raffle_ticket(self):
        """Registra la venta del ticket: asigna comprador, genera semilla aleatoria,
        y verifica si el sorteo se completó (último ticket vendido).
        Requerimiento: cada venta genera un valor aleatorio acumulativo."""
        self.ensure_one()
        ticket = self.raffle_ticket_id
        raffle = ticket.raffle_id
        random_value = random.uniform(0, 1000000)

        ticket.write({
            'state': 'sold',
            'partner_id': self.order_id.partner_id.id,
            'sale_order_line_id': self.id,
            'purchase_date': fields.Datetime.now(),
            'random_value': random_value,
        })
        raffle.random_seed_sum += random_value

        # Verificar si se vendieron todos los tickets → completar sorteo
        if not raffle.ticket_ids.filtered(lambda t: t.state == 'available'):
            raffle._on_all_tickets_sold()


class SaleOrder(models.Model):
    """Herencia de sale.order para mostrar tickets de rifa vinculados."""
    _inherit = 'sale.order'

    raffle_ticket_count = fields.Integer(
        string='Tickets de Rifa',
        compute='_compute_raffle_ticket_count',
    )

    def _compute_raffle_ticket_count(self):
        for order in self:
            order.raffle_ticket_count = len(
                order.order_line.filtered(lambda l: l.raffle_ticket_id)
            )
