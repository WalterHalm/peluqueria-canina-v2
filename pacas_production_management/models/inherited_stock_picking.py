from odoo import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    pacas_container_id = fields.Many2one(
        'pacas.container', 'Contenedor',
        index='btree_not_null', check_company=True,
        help="Contenedor relacionado a esta transferencia")
