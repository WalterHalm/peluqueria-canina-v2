from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    re_latitude = fields.Char(string="Latitud", help="Ej: -30.767007")
    re_longitude = fields.Char(string="Longitud", help="Ej: -57.990718")
    re_zone = fields.Char(string="Zona / Barrio")
    re_address = fields.Char(string="Dirección")
    re_show_on_map = fields.Boolean(string="Mostrar en mapa", default=True)
