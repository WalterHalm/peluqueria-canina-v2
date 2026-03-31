from datetime import timedelta

from odoo import _, api, fields, models


class RaffleTicket(models.Model):
    """Ticket numerado de un sorteo.
    Cada sorteo genera N tickets con números secuenciales.
    El cliente puede seleccionar su número favorito en la cuadrícula.
    Requerimiento: cuadrícula 10x10, verde=disponible, rojo=vendido.
    """
    _name = 'raffle.ticket'
    _description = 'Ticket de Sorteo'
    _order = 'number asc'
    _rec_name = 'name'

    name = fields.Char(string='Código', required=True, index=True)
    raffle_id = fields.Many2one(
        'raffle.raffle',
        string='Sorteo',
        required=True,
        ondelete='cascade',
        index=True,
    )
    number = fields.Integer(string='Número', required=True, index=True)
    state = fields.Selection([
        ('available', 'Disponible'),
        ('sold', 'Vendido'),
        ('cancelled', 'Cancelado'),
        ('winner', 'Ganador'),
    ], string='Estado', default='available', required=True, index=True)

    # --- Datos de compra ---

    partner_id = fields.Many2one('res.partner', string='Comprador')
    sale_order_line_id = fields.Many2one('sale.order.line', string='Línea de Venta')
    purchase_date = fields.Datetime(string='Fecha de Compra')
    cancellation_deadline = fields.Datetime(
        string='Límite de Cancelación',
        compute='_compute_cancellation_deadline',
        store=True,
    )
    can_cancel = fields.Boolean(
        string='Puede Cancelar',
        compute='_compute_can_cancel',
    )
    random_value = fields.Float(string='Valor Aleatorio', default=0.0)

    # --- Campos relacionados (para mostrar en vistas sin joins manuales) ---

    raffle_state = fields.Selection(related='raffle_id.state', string='Estado Sorteo')
    product_name = fields.Char(related='raffle_id.product_id.name', string='Producto')
    ticket_price = fields.Float(related='raffle_id.ticket_price', string='Precio')
    currency_id = fields.Many2one(related='raffle_id.currency_id')

    _sql_constraints = [
        ('unique_raffle_number', 'UNIQUE(raffle_id, number)',
         'El número de ticket debe ser único por sorteo.'),
    ]

    # --- Campos computados ---

    @api.depends('purchase_date')
    def _compute_cancellation_deadline(self):
        """Requerimiento: el cliente puede cancelar dentro de las 24 horas
        posteriores a la compra. Pasado ese plazo, no se permite cancelar."""
        for rec in self:
            rec.cancellation_deadline = rec.purchase_date + timedelta(hours=24) if rec.purchase_date else False

    def _compute_can_cancel(self):
        """Determina si el ticket aún está dentro de la ventana de cancelación.
        Se usa para mostrar/ocultar el botón de cancelar en portal y backend."""
        now = fields.Datetime.now()
        for rec in self:
            rec.can_cancel = (
                rec.state == 'sold'
                and rec.cancellation_deadline
                and now < rec.cancellation_deadline
            )

    # --- Acciones ---

    def action_cancel_ticket(self):
        """Cancelar ticket: lo libera y lo devuelve al pool de disponibles.
        Requerimiento del cliente:
        - Ticket vuelve a estado 'disponible'
        - Se elimina el comprador de la lista de participantes
        - Se resta el valor aleatorio de la semilla del sorteo
        - El reembolso se gestiona como nota de crédito (Etapa 2)"""
        for rec in self:
            if not rec.can_cancel:
                continue
            raffle = rec.raffle_id
            raffle.random_seed_sum -= rec.random_value
            rec.write({
                'state': 'available',
                'partner_id': False,
                'sale_order_line_id': False,
                'purchase_date': False,
                'random_value': 0.0,
            })
