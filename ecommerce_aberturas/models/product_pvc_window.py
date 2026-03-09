from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_pvc_window = fields.Boolean('Es Ventana PVC')
    series_id = fields.Many2one('product.series', 'Serie')
    
    width = fields.Float('Ancho (cm)')
    height = fields.Float('Alto (cm)')
    custom_size = fields.Boolean('Medida Personalizada')
    
    glass_type = fields.Selection([
        ('simple', 'Simple'),
        ('double', 'Doble'),
        ('triple', 'Triple'),
        ('low_e', 'Bajo Emisivo')
    ], string='Tipo Vidrio')
    
    thermal_insulation = fields.Char('Aislamiento Térmico')
    acoustic_insulation = fields.Char('Aislamiento Acústico')
    security_level = fields.Selection([
        ('basic', 'Básico'),
        ('medium', 'Medio'),
        ('high', 'Alto'),
        ('maximum', 'Máximo')
    ], string='Nivel Seguridad')
    
    technical_sheet = fields.Binary('Ficha Técnica PDF')
    technical_sheet_filename = fields.Char('Nombre Archivo')
    
    price_distributor = fields.Float('Precio Distribuidor')
    min_quantity_distributor = fields.Integer('Cantidad Mínima Distribuidor', default=10)
    
    @api.onchange('series_id')
    def _onchange_series_id(self):
        if self.series_id:
            self.is_pvc_window = True
