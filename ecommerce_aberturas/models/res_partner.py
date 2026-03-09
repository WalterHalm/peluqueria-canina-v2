from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_type = fields.Selection([
        ('individual', 'Particular'),
        ('distributor', 'Distribuidor')
    ], string='Tipo Cliente', default='individual')
    
    distributor_code = fields.Char('Código Distribuidor')
    discount_rate = fields.Float('% Descuento')
