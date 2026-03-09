from odoo import models, fields, api

class ProductSeries(models.Model):
    _name = 'product.series'
    _description = 'Serie de Ventanas PVC'
    _order = 'sequence, name'

    name = fields.Char('Nombre Serie', required=True)
    code = fields.Char('Código', required=True)
    sequence = fields.Integer('Secuencia', default=10)
    description = fields.Html('Descripción')
    image = fields.Image('Imagen')
    active = fields.Boolean('Activo', default=True)
    
    quality_level = fields.Selection([
        ('economic', 'Económica'),
        ('standard', 'Estándar'),
        ('premium', 'Premium'),
        ('luxury', 'Luxury')
    ], string='Nivel Calidad', required=True)
    
    product_ids = fields.One2many('product.template', 'series_id', 'Productos')
    product_count = fields.Integer('Nº Productos', compute='_compute_product_count')
    
    @api.depends('product_ids')
    def _compute_product_count(self):
        for series in self:
            series.product_count = len(series.product_ids)
    
    def action_view_products(self):
        self.ensure_one()
        return {
            'name': f'Productos - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'product.template',
            'view_mode': 'kanban,list,form',
            'domain': [('series_id', '=', self.id)],
            'context': {'default_series_id': self.id, 'default_is_pvc_window': True},
        }
