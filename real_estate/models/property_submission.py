from odoo import fields, models


class PropertySubmission(models.Model):
    _name = 'real.estate.property.submission'
    _description = 'Solicitud de Captación de Propiedad'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string="Nombre de la Propiedad", required=True, tracking=True)
    state = fields.Selection([
        ('new', 'Nueva'),
        ('reviewing', 'En Revisión'),
        ('approved', 'Aprobada'),
        ('rejected', 'Rechazada'),
    ], default='new', tracking=True)

    # Owner data
    owner_name = fields.Char(string="Nombre del Propietario", required=True)
    owner_email = fields.Char(string="Email", required=True)
    owner_phone = fields.Char(string="Teléfono", required=True)
    partner_id = fields.Many2one('res.partner', string="Contacto Odoo")

    # Property data
    property_type = fields.Selection([
        ('apartment', 'Apartamento'),
        ('house', 'Casa'),
        ('villa', 'Villa'),
        ('room', 'Habitación'),
    ], string="Tipo", required=True)
    listing_type = fields.Selection([
        ('rent', 'Alquiler'),
        ('sale', 'Venta'),
        ('both', 'Ambos'),
    ], string="Para", required=True)
    address = fields.Char(string="Dirección", required=True)
    zone = fields.Char(string="Zona / Barrio")
    bedrooms = fields.Integer(string="Habitaciones")
    capacity = fields.Integer(string="Capacidad (personas)")
    price_per_night = fields.Float(string="Precio por noche (referencia)")
    description = fields.Text(string="Descripción")
    amenities = fields.Char(string="Amenidades (separadas por coma)")

    # Images
    image_1 = fields.Binary(string="Foto 1")
    image_2 = fields.Binary(string="Foto 2")
    image_3 = fields.Binary(string="Foto 3")

    # Generated product
    product_id = fields.Many2one('product.template', string="Producto Creado", readonly=True)

    def action_approve(self):
        self.ensure_one()
        product = self.env['product.template'].create({
            'name': self.name,
            'type': 'consu',
            'rent_ok': True,
            'sale_ok': self.listing_type in ('sale', 'both'),
            'description_sale': self.description or '',
            're_address': self.address,
            're_zone': self.zone or '',
            'image_1920': self.image_1,
        })
        self.write({'state': 'approved', 'product_id': product.id})

    def action_reject(self):
        self.write({'state': 'rejected'})
