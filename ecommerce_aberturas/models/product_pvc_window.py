from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_pvc_window = fields.Boolean('Es Ventana PVC')
    
    width = fields.Float('Ancho (cm)')
    height = fields.Float('Alto (cm)')
    custom_size = fields.Boolean('Medida Personalizada')
    
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
