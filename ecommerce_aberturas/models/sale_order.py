from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    tracking_status = fields.Selection([
        ('confirmed', 'Pedido Confirmado'),
        ('production', 'En Producción'),
        ('quality', 'Control de Calidad'),
        ('packaging', 'Empaquetado'),
        ('shipped', 'Enviado'),
        ('in_transit', 'En Tránsito'),
        ('delivered', 'Entregado')
    ], string='Estado Seguimiento', default='confirmed')
    
    tracking_url = fields.Char('URL Seguimiento')
    estimated_delivery = fields.Date('Entrega Estimada')
    customer_type = fields.Selection(related='partner_id.customer_type', store=True)
