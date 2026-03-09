from odoo import models, fields

class CustomerTestimonial(models.Model):
    _name = 'customer.testimonial'
    _description = 'Testimonio de Cliente'
    _order = 'date desc, id desc'

    name = fields.Char('Nombre Cliente', required=True)
    partner_id = fields.Many2one('res.partner', 'Cliente')
    email = fields.Char('Email')
    
    testimonial = fields.Text('Testimonio', required=True)
    rating = fields.Selection([
        ('1', '⭐'),
        ('2', '⭐⭐'),
        ('3', '⭐⭐⭐'),
        ('4', '⭐⭐⭐⭐'),
        ('5', '⭐⭐⭐⭐⭐')
    ], string='Valoración', required=True, default='5')
    
    image = fields.Image('Foto Cliente')
    product_id = fields.Many2one('product.template', 'Producto')
    
    date = fields.Date('Fecha', default=fields.Date.today)
    published = fields.Boolean('Publicado', default=False)
    featured = fields.Boolean('Destacado')
    active = fields.Boolean('Activo', default=True)
    
    verified_purchase = fields.Boolean('Compra Verificada')
    sale_order_id = fields.Many2one('sale.order', 'Pedido')
