# Documento de Desarrollo por Etapas — Real Estate Odoo 19

## ETAPA 1 — WhatsApp Flotante + Redes Sociales
## ETAPA 2 — Mapa con Leaflet.js
## ETAPA 3 — Payment Provider Bold
## ETAPA 4 — Portal de Propietarios
## ETAPA 5 — Sincronización iCal Airbnb/Booking


---

## ETAPA 1 — WhatsApp Flotante + Redes Sociales

**Complejidad:** Baja | **Tiempo estimado:** 1-2 días | **Dependencias:** Ninguna

### Qué se desarrolla
- Botón flotante de WhatsApp en todas las páginas del sitio web
- Botones de redes sociales flotantes (Facebook, Instagram, TikTok)
- Configuración desde el backend (número de WhatsApp, URLs de redes)

### Archivos a crear en `real_estate/`

```
real_estate/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── res_config_settings.py      # Campos: whatsapp_number, facebook_url, instagram_url
├── views/
│   └── res_config_settings_views.xml
├── templates/
│   └── whatsapp_social.xml         # Template QWeb con botones flotantes
└── static/
    └── src/
        └── css/
            └── floating_buttons.css
```

### 1.1 `__manifest__.py`

```python
{
    'name': 'Real Estate',
    'version': '1.0',
    'category': 'Real Estate',
    'depends': ['website', 'website_sale', 'sale_renting'],
    'data': [
        'views/res_config_settings_views.xml',
        'templates/whatsapp_social.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'real_estate/static/src/css/floating_buttons.css',
        ],
    },
    'license': 'LGPL-3',
}
```

### 1.2 `models/res_config_settings.py`

```python
from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    whatsapp_number = fields.Char(
        string="Número WhatsApp",
        config_parameter='real_estate.whatsapp_number',
    )
    facebook_url = fields.Char(
        string="URL Facebook",
        config_parameter='real_estate.facebook_url',
    )
    instagram_url = fields.Char(
        string="URL Instagram",
        config_parameter='real_estate.instagram_url',
    )
    tiktok_url = fields.Char(
        string="URL TikTok",
        config_parameter='real_estate.tiktok_url',
    )
```

### 1.3 `templates/whatsapp_social.xml`

```xml
<odoo>
    <template id="whatsapp_floating_button" inherit_id="website.layout" name="WhatsApp Flotante">
        <xpath expr="//div[@id='wrapwrap']" position="inside">
            <div class="re_floating_buttons">
                <t t-set="wa_number" t-value="request.env['ir.config_parameter'].sudo().get_param('real_estate.whatsapp_number')"/>
                <t t-set="fb_url" t-value="request.env['ir.config_parameter'].sudo().get_param('real_estate.facebook_url')"/>
                <t t-set="ig_url" t-value="request.env['ir.config_parameter'].sudo().get_param('real_estate.instagram_url')"/>

                <a t-if="wa_number"
                   t-attf-href="https://wa.me/#{wa_number}"
                   class="re_btn_whatsapp"
                   target="_blank" rel="noopener">
                    <i class="fa fa-whatsapp"/>
                </a>
                <a t-if="fb_url" t-att-href="fb_url" class="re_btn_facebook" target="_blank" rel="noopener">
                    <i class="fa fa-facebook"/>
                </a>
                <a t-if="ig_url" t-att-href="ig_url" class="re_btn_instagram" target="_blank" rel="noopener">
                    <i class="fa fa-instagram"/>
                </a>
            </div>
        </xpath>
    </template>
</odoo>
```

### 1.4 `static/src/css/floating_buttons.css`

```css
.re_floating_buttons {
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 9999;
    display: flex;
    flex-direction: column;
    gap: 10px;
}
.re_floating_buttons a {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 22px;
    text-decoration: none;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    transition: transform 0.2s;
}
.re_floating_buttons a:hover { transform: scale(1.1); }
.re_btn_whatsapp  { background: #25D366; }
.re_btn_facebook  { background: #1877F2; }
.re_btn_instagram { background: #E1306C; }
```

### 1.5 Configuración en Backend
Ruta: Ajustes → Real Estate → Ingresar número WhatsApp (formato: 573001234567) y URLs de redes.


---

## ETAPA 2 — Mapa con Leaflet.js (Filtro por Zona)

**Complejidad:** Media | **Tiempo estimado:** 3-5 días | **Dependencias:** Etapa 1 (módulo base creado)

### Qué se desarrolla
- Campos de coordenadas (latitud/longitud) y zona en el modelo `product.template`
- Página `/mapa` con mapa Leaflet mostrando todas las propiedades de alquiler
- Marcadores clicables que abren popup con foto, nombre y precio
- Filtro por zona (barrio/sector) en el mapa
- Endpoint JSON que devuelve propiedades con coordenadas

### Por qué Leaflet y no Google Maps
- Leaflet es open source, sin costo ni API key
- Usa OpenStreetMap como tiles (gratuito)
- Suficiente para mostrar marcadores y filtrar por zona
- Google Maps requiere tarjeta de crédito y tiene costo por uso

### 2.1 Modelo — `models/product_template.py`

```python
from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    re_latitude = fields.Float(string="Latitud", digits=(10, 7))
    re_longitude = fields.Float(string="Longitud", digits=(10, 7))
    re_zone = fields.Char(string="Zona / Barrio")
    re_address = fields.Char(string="Dirección")
    re_show_on_map = fields.Boolean(string="Mostrar en mapa", default=True)
```

### 2.2 Vista Backend — `views/product_template_views.xml`

```xml
<odoo>
    <record id="product_template_re_map_view" model="ir.ui.view">
        <field name="name">product.template.re.map</field>
        <field name="model">product.template</field>
        <field name="inherit_id" ref="product.product_template_form_view"/>
        <field name="arch" type="xml">
            <xpath expr="//page[@name='sales']" position="after">
                <page string="Ubicación" name="re_location">
                    <group>
                        <field name="re_address"/>
                        <field name="re_zone"/>
                        <field name="re_latitude"/>
                        <field name="re_longitude"/>
                        <field name="re_show_on_map"/>
                    </group>
                </page>
            </xpath>
        </field>
    </record>
</odoo>
```

### 2.3 Controller — `controllers/map.py`

```python
import json
from odoo import http
from odoo.http import request

class RealEstateMapController(http.Controller):

    @http.route('/mapa', type='http', auth='public', website=True)
    def map_page(self, zone=None, **kwargs):
        zones = request.env['product.template'].sudo().search_read(
            [('rent_ok', '=', True), ('re_zone', '!=', False), ('website_published', '=', True)],
            ['re_zone']
        )
        zone_list = sorted(set(z['re_zone'] for z in zones))
        return request.render('real_estate.map_page', {
            'zones': zone_list,
            'selected_zone': zone,
        })

    @http.route('/mapa/propiedades.json', type='http', auth='public', website=True)
    def map_properties_json(self, zone=None, **kwargs):
        domain = [
            ('rent_ok', '=', True),
            ('re_show_on_map', '=', True),
            ('re_latitude', '!=', 0),
            ('re_longitude', '!=', 0),
            ('website_published', '=', True),
        ]
        if zone:
            domain.append(('re_zone', '=', zone))

        products = request.env['product.template'].sudo().search(domain)
        data = []
        for p in products:
            data.append({
                'id': p.id,
                'name': p.name,
                'lat': p.re_latitude,
                'lng': p.re_longitude,
                'zone': p.re_zone or '',
                'address': p.re_address or '',
                'price': p.display_price or '',
                'url': '/shop/%s' % p.website_slug if hasattr(p, 'website_slug') else '/shop',
                'image_url': '/web/image/product.template/%d/image_128' % p.id,
            })
        return request.make_response(
            json.dumps(data),
            headers=[('Content-Type', 'application/json')]
        )
```

### 2.4 Template — `templates/map_page.xml`

```xml
<odoo>
    <template id="map_page" name="Mapa de Propiedades">
        <t t-call="website.layout">
            <div id="wrap">
                <div class="container-fluid py-3">
                    <h2 class="text-center mb-3">Propiedades en Alquiler</h2>

                    <!-- Filtro por zona -->
                    <div class="d-flex justify-content-center gap-2 flex-wrap mb-3">
                        <a href="/mapa" t-attf-class="btn btn-sm #{'btn-primary' if not selected_zone else 'btn-outline-secondary'}">
                            Todas
                        </a>
                        <t t-foreach="zones" t-as="zone">
                            <a t-att-href="'/mapa?zone=' + zone"
                               t-attf-class="btn btn-sm #{'btn-primary' if selected_zone == zone else 'btn-outline-secondary'}">
                                <t t-out="zone"/>
                            </a>
                        </t>
                    </div>

                    <!-- Mapa -->
                    <div id="re_map" style="height: 550px; border-radius: 12px;"/>
                </div>
            </div>

            <!-- Leaflet CSS/JS desde CDN -->
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"/>
            <script type="text/javascript">
                (function() {
                    var map = L.map('re_map').setView([4.6097, -74.0817], 12);
                    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                        attribution: '© OpenStreetMap'
                    }).addTo(map);

                    var zone = '<t t-out="selected_zone or &quot;&quot;"/>';
                    var url = '/mapa/propiedades.json' + (zone ? '?zone=' + encodeURIComponent(zone) : '');

                    fetch(url)
                        .then(function(r) { return r.json(); })
                        .then(function(props) {
                            props.forEach(function(p) {
                                var marker = L.marker([p.lat, p.lng]).addTo(map);
                                marker.bindPopup(
                                    '<div style="min-width:160px">' +
                                    '<img src="' + p.image_url + '" style="width:100%;border-radius:6px;margin-bottom:6px"/>' +
                                    '<strong>' + p.name + '</strong><br/>' +
                                    '<small>' + p.address + '</small><br/>' +
                                    '<span class="text-primary">' + p.price + '</span><br/>' +
                                    '<a href="' + p.url + '" class="btn btn-sm btn-primary mt-1">Ver propiedad</a>' +
                                    '</div>'
                                );
                            });
                            if (props.length > 0) {
                                var bounds = props.map(function(p) { return [p.lat, p.lng]; });
                                map.fitBounds(bounds, {padding: [30, 30]});
                            }
                        });
                })();
            </script>
        </t>
    </template>
</odoo>
```

### 2.5 Seguridad — `security/ir.model.access.csv`

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
```
(Los campos re_* se agregan a product.template que ya tiene sus propios permisos, no se necesitan nuevos registros de acceso para estos campos.)

### 2.6 Agregar al menú del sitio web
En el editor del sitio web, agregar en el menú: **Mapa** → `/mapa`


---

## ETAPA 3 — Payment Provider Bold

**Complejidad:** Alta | **Tiempo estimado:** 5-8 días | **Dependencias:** Etapa 1

### Qué es Bold
Bold es una pasarela de pagos colombiana que permite cobrar con tarjetas débito/crédito, PSE y otros métodos locales. Usa un flujo de **redirección**: el usuario es enviado al checkout de Bold, paga, y Bold redirige de vuelta a Odoo con el resultado.

### Arquitectura del módulo `payment_bold`
Siguiendo exactamente el patrón de `payment_mercado_pago` y `payment_stripe` de Odoo 19:

```
payment_bold/
├── __init__.py
├── __manifest__.py
├── const.py                          # URLs de API, códigos de estado
├── models/
│   ├── __init__.py
│   ├── payment_provider.py           # Campos Bold + métodos de request
│   └── payment_transaction.py        # Lógica de creación y verificación de transacción
├── controllers/
│   ├── __init__.py
│   └── main.py                       # Webhook endpoint para notificaciones de Bold
├── views/
│   ├── payment_bold_templates.xml    # Formulario de redirección
│   ├── payment_form_templates.xml    # Hereda payment.checkout
│   └── payment_provider_views.xml    # Campos Bold en el form del proveedor
├── data/
│   └── payment_provider_data.xml     # Registro inicial del proveedor
└── static/src/
    └── js/
        └── payment_form.js           # JS para manejar el redirect
```

### 3.1 `const.py`

```python
BOLD_API_URL = 'https://integrations.bold.co'
BOLD_CHECKOUT_URL = 'https://checkout.bold.co/payment/link'

PAYMENT_STATUS_MAPPING = {
    'approved': 'done',
    'pending': 'pending',
    'rejected': 'cancel',
    'failed': 'cancel',
    'voided': 'cancel',
}

DEFAULT_PAYMENT_METHOD_CODES = {
    'card',
    'pse',
}
```

### 3.2 `models/payment_provider.py`

```python
import hashlib
import hmac
from odoo import fields, models
from odoo.addons.payment_bold import const

class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('bold', 'Bold')],
        ondelete={'bold': 'set default'}
    )
    bold_api_key = fields.Char(
        string="Bold API Key (Secret Key)",
        required_if_provider='bold',
        groups='base.group_system',
    )
    bold_integrity_key = fields.Char(
        string="Bold Integrity Key",
        required_if_provider='bold',
        groups='base.group_system',
    )

    def _compute_feature_support_fields(self):
        super()._compute_feature_support_fields()
        self.filtered(lambda p: p.code == 'bold').update({
            'support_refund': 'none',
            'support_tokenization': False,
        })

    def _get_default_payment_method_codes(self):
        self.ensure_one()
        if self.code != 'bold':
            return super()._get_default_payment_method_codes()
        return const.DEFAULT_PAYMENT_METHOD_CODES

    def _bold_compute_signature(self, reference, amount_in_cents, currency):
        """Compute the integrity hash required by Bold."""
        self.ensure_one()
        raw = f"{reference}{amount_in_cents}{currency}{self.bold_integrity_key}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def _build_request_url(self, endpoint, **kwargs):
        if self.code != 'bold':
            return super()._build_request_url(endpoint, **kwargs)
        return f"{const.BOLD_API_URL}{endpoint}"

    def _build_request_headers(self, method, endpoint, payload, **kwargs):
        if self.code != 'bold':
            return super()._build_request_headers(method, endpoint, payload, **kwargs)
        return {
            'Authorization': f'x-api-key {self.bold_api_key}',
            'Content-Type': 'application/json',
        }
```

### 3.3 `models/payment_transaction.py`

```python
import logging
from odoo import _, models
from odoo.addons.payment_bold import const

_logger = logging.getLogger(__name__)

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        self.ensure_one()
        if self.provider_code != 'bold':
            return super()._get_specific_rendering_values(processing_values)

        amount_in_cents = int(round(self.amount * 100))
        currency = self.currency_id.name
        signature = self.provider_id._bold_compute_signature(
            self.reference, amount_in_cents, currency
        )
        return {
            'api_url': const.BOLD_CHECKOUT_URL,
            'amount_in_cents': amount_in_cents,
            'currency': currency,
            'reference': self.reference,
            'integrity_signature': signature,
            'redirect_url': self.provider_id.get_base_url() + '/payment/bold/return',
        }

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'bold' or len(tx) == 1:
            return tx
        reference = notification_data.get('order_id') or notification_data.get('reference')
        tx = self.search([('reference', '=', reference), ('provider_code', '=', 'bold')])
        return tx

    def _process_notification_data(self, notification_data):
        self.ensure_one()
        if self.provider_code != 'bold':
            return super()._process_notification_data(notification_data)

        bold_status = notification_data.get('transaction', {}).get('status', '').lower()
        odoo_status = const.PAYMENT_STATUS_MAPPING.get(bold_status, 'pending')

        if odoo_status == 'done':
            self._set_done()
        elif odoo_status == 'pending':
            self._set_pending()
        elif odoo_status == 'cancel':
            self._set_canceled()
        else:
            _logger.warning("Bold: estado desconocido %s para tx %s", bold_status, self.reference)
```

### 3.4 `controllers/main.py`

```python
import logging
import json
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class BoldController(http.Controller):

    @http.route('/payment/bold/return', type='http', auth='public', website=True, csrf=False)
    def bold_return(self, **data):
        """Maneja el retorno del usuario desde Bold Checkout."""
        _logger.info("Bold return: %s", data)
        request.env['payment.transaction'].sudo()._handle_notification_data('bold', data)
        return request.redirect('/payment/status')

    @http.route('/payment/bold/webhook', type='http', auth='public', csrf=False, methods=['POST'])
    def bold_webhook(self, **kwargs):
        """Recibe notificaciones asíncronas de Bold."""
        try:
            data = json.loads(request.httprequest.data)
            _logger.info("Bold webhook: %s", data)
            request.env['payment.transaction'].sudo()._handle_notification_data('bold', data)
        except Exception as e:
            _logger.exception("Error procesando webhook Bold: %s", e)
        return request.make_response('OK', headers=[('Content-Type', 'text/plain')])
```

### 3.5 `views/payment_bold_templates.xml`

```xml
<odoo>
    <template id="redirect_form" key="payment_bold.redirect_form">
        <form method="post" t-att-action="rendering_values['api_url']">
            <input type="hidden" name="order_id" t-att-value="rendering_values['reference']"/>
            <input type="hidden" name="amount" t-att-value="rendering_values['amount_in_cents']"/>
            <input type="hidden" name="currency" t-att-value="rendering_values['currency']"/>
            <input type="hidden" name="integrity_signature" t-att-value="rendering_values['integrity_signature']"/>
            <input type="hidden" name="redirect_url" t-att-value="rendering_values['redirect_url']"/>
            <button type="submit" class="btn btn-primary">Pagar con Bold</button>
        </form>
    </template>
</odoo>
```

### 3.6 `data/payment_provider_data.xml`

```xml
<odoo>
    <record id="payment_provider_bold" model="payment.provider">
        <field name="name">Bold</field>
        <field name="code">bold</field>
        <field name="state">disabled</field>
        <field name="is_published" eval="False"/>
        <field name="redirect_form_view_id" ref="payment_bold.redirect_form"/>
    </record>
</odoo>
```

### 3.7 Configuración post-instalación
1. Ir a Facturación → Proveedores de Pago → Bold
2. Estado: Test (para pruebas) o Enabled
3. Ingresar Bold API Key (Secret Key del dashboard Bold)
4. Ingresar Bold Integrity Key
5. Configurar URL del webhook en el dashboard de Bold: `https://tudominio.com/payment/bold/webhook`
6. Probar con una transacción de prueba

### NOTA IMPORTANTE sobre Bold API
Bold tiene dos tipos de integración:
- **Payment Link (Checkout hosted):** Redirección al checkout de Bold — más simple, recomendado para empezar
- **API directa:** Integración inline — más compleja, requiere certificación PCI

Este desarrollo implementa el flujo de **Payment Link** que es el más rápido de implementar y el que Bold recomienda para integraciones nuevas. Consultar la documentación oficial de Bold en `https://developers.bold.co` para obtener las credenciales y confirmar los endpoints exactos de la versión actual de su API.


---

## ETAPA 4 — Portal de Propietarios (Carga de Propiedades)

**Complejidad:** Alta | **Tiempo estimado:** 5-7 días | **Dependencias:** Etapas 1 y 2

### Qué se desarrolla
- Modelo `real.estate.property.submission` para propiedades enviadas por propietarios
- Formulario web en `/captacion` donde propietarios completan datos de su propiedad
- Subida de fotos desde el formulario web
- Flujo de aprobación: el admin revisa y aprueba → se crea el producto en el catálogo
- Vista backend para gestionar las solicitudes de captación

### Flujo completo
```
Propietario llena formulario web (/captacion)
        ↓
Se crea real.estate.property.submission (estado: nuevo)
        ↓
Admin recibe notificación por email
        ↓
Admin revisa en backend → Aprueba o Rechaza
        ↓
Si aprueba → Se crea product.template con rent_ok=True automáticamente
        ↓
Propietario recibe email de confirmación
```

### 4.1 Modelo — `models/property_submission.py`

```python
from odoo import api, fields, models

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

    # Datos del propietario
    owner_name = fields.Char(string="Nombre del Propietario", required=True)
    owner_email = fields.Char(string="Email", required=True)
    owner_phone = fields.Char(string="Teléfono", required=True)
    partner_id = fields.Many2one('res.partner', string="Contacto Odoo")

    # Datos de la propiedad
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

    # Imágenes
    image_1 = fields.Binary(string="Foto 1")
    image_2 = fields.Binary(string="Foto 2")
    image_3 = fields.Binary(string="Foto 3")

    # Producto generado
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
        self._send_owner_notification('approved')

    def action_reject(self):
        self.write({'state': 'rejected'})
        self._send_owner_notification('rejected')

    def _send_owner_notification(self, result):
        template_ref = (
            'real_estate.email_submission_approved'
            if result == 'approved'
            else 'real_estate.email_submission_rejected'
        )
        template = self.env.ref(template_ref, raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)
```

### 4.2 Controller — `controllers/captacion.py`

```python
from odoo import http
from odoo.http import request

class CaptacionController(http.Controller):

    @http.route('/captacion', type='http', auth='public', website=True)
    def captacion_page(self, **kwargs):
        return request.render('real_estate.captacion_page', {})

    @http.route('/captacion/submit', type='http', auth='public', website=True, methods=['POST'], csrf=True)
    def captacion_submit(self, **post):
        vals = {
            'name': post.get('property_name', ''),
            'owner_name': post.get('owner_name', ''),
            'owner_email': post.get('owner_email', ''),
            'owner_phone': post.get('owner_phone', ''),
            'property_type': post.get('property_type', 'apartment'),
            'listing_type': post.get('listing_type', 'rent'),
            'address': post.get('address', ''),
            'zone': post.get('zone', ''),
            'bedrooms': int(post.get('bedrooms', 0) or 0),
            'capacity': int(post.get('capacity', 0) or 0),
            'price_per_night': float(post.get('price_per_night', 0) or 0),
            'description': post.get('description', ''),
            'amenities': post.get('amenities', ''),
        }

        # Procesar imágenes subidas
        for i in range(1, 4):
            img_file = request.httprequest.files.get(f'image_{i}')
            if img_file and img_file.filename:
                import base64
                vals[f'image_{i}'] = base64.b64encode(img_file.read())

        request.env['real.estate.property.submission'].sudo().create(vals)
        return request.render('real_estate.captacion_thanks', {})
```

### 4.3 Template — `templates/captacion.xml`

```xml
<odoo>
    <template id="captacion_page" name="Captación de Propiedades">
        <t t-call="website.layout">
            <div id="wrap" class="container py-5">
                <h2 class="text-center mb-4">¿Tenés una propiedad? ¡Administrámosla!</h2>
                <div class="row justify-content-center">
                    <div class="col-lg-8">
                        <form action="/captacion/submit" method="post" enctype="multipart/form-data">
                            <input type="hidden" name="csrf_token" t-att-value="request.csrf_token()"/>

                            <h5 class="mt-3">Tus datos</h5>
                            <div class="row g-3">
                                <div class="col-md-4">
                                    <input name="owner_name" class="form-control" placeholder="Tu nombre *" required="1"/>
                                </div>
                                <div class="col-md-4">
                                    <input name="owner_email" type="email" class="form-control" placeholder="Email *" required="1"/>
                                </div>
                                <div class="col-md-4">
                                    <input name="owner_phone" class="form-control" placeholder="Teléfono *" required="1"/>
                                </div>
                            </div>

                            <h5 class="mt-4">Datos de la propiedad</h5>
                            <div class="row g-3">
                                <div class="col-md-6">
                                    <input name="property_name" class="form-control" placeholder="Nombre de la propiedad *" required="1"/>
                                </div>
                                <div class="col-md-3">
                                    <select name="property_type" class="form-select">
                                        <option value="apartment">Apartamento</option>
                                        <option value="house">Casa</option>
                                        <option value="villa">Villa</option>
                                        <option value="room">Habitación</option>
                                    </select>
                                </div>
                                <div class="col-md-3">
                                    <select name="listing_type" class="form-select">
                                        <option value="rent">Alquiler</option>
                                        <option value="sale">Venta</option>
                                        <option value="both">Ambos</option>
                                    </select>
                                </div>
                                <div class="col-md-8">
                                    <input name="address" class="form-control" placeholder="Dirección *" required="1"/>
                                </div>
                                <div class="col-md-4">
                                    <input name="zone" class="form-control" placeholder="Zona / Barrio"/>
                                </div>
                                <div class="col-md-3">
                                    <input name="bedrooms" type="number" class="form-control" placeholder="Habitaciones" min="0"/>
                                </div>
                                <div class="col-md-3">
                                    <input name="capacity" type="number" class="form-control" placeholder="Capacidad (personas)" min="0"/>
                                </div>
                                <div class="col-md-6">
                                    <input name="price_per_night" type="number" class="form-control" placeholder="Precio por noche (referencia)"/>
                                </div>
                                <div class="col-12">
                                    <textarea name="description" class="form-control" rows="4" placeholder="Descripción de la propiedad"/>
                                </div>
                                <div class="col-12">
                                    <input name="amenities" class="form-control" placeholder="Amenidades (ej: WiFi, Piscina, A/C)"/>
                                </div>
                            </div>

                            <h5 class="mt-4">Fotos</h5>
                            <div class="row g-3">
                                <div class="col-md-4">
                                    <input name="image_1" type="file" class="form-control" accept="image/*"/>
                                </div>
                                <div class="col-md-4">
                                    <input name="image_2" type="file" class="form-control" accept="image/*"/>
                                </div>
                                <div class="col-md-4">
                                    <input name="image_3" type="file" class="form-control" accept="image/*"/>
                                </div>
                            </div>

                            <div class="text-center mt-4">
                                <button type="submit" class="btn btn-primary btn-lg px-5">
                                    Enviar mi propiedad
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </t>
    </template>

    <template id="captacion_thanks" name="Gracias por tu envío">
        <t t-call="website.layout">
            <div id="wrap" class="container py-5 text-center">
                <i class="fa fa-check-circle fa-4x text-success mb-3"/>
                <h2>¡Gracias! Recibimos tu propiedad.</h2>
                <p class="lead">Nos pondremos en contacto a la brevedad para coordinar la visita.</p>
                <a href="/" class="btn btn-primary mt-3">Volver al inicio</a>
            </div>
        </t>
    </template>
</odoo>
```

### 4.4 Vista Backend — `views/property_submission_views.xml`

```xml
<odoo>
    <record id="view_property_submission_list" model="ir.ui.view">
        <field name="name">real.estate.property.submission.list</field>
        <field name="model">real.estate.property.submission</field>
        <field name="arch" type="xml">
            <list string="Solicitudes de Captación" decoration-success="state=='approved'" decoration-danger="state=='rejected'">
                <field name="create_date"/>
                <field name="name"/>
                <field name="owner_name"/>
                <field name="owner_phone"/>
                <field name="property_type"/>
                <field name="listing_type"/>
                <field name="zone"/>
                <field name="state"/>
            </list>
        </field>
    </record>

    <record id="view_property_submission_form" model="ir.ui.view">
        <field name="name">real.estate.property.submission.form</field>
        <field name="model">real.estate.property.submission</field>
        <field name="arch" type="xml">
            <form string="Solicitud de Captación">
                <header>
                    <button name="action_approve" string="Aprobar y Crear Producto" type="object"
                            class="btn-primary" invisible="state != 'new' and state != 'reviewing'"/>
                    <button name="action_reject" string="Rechazar" type="object"
                            invisible="state != 'new' and state != 'reviewing'"/>
                    <field name="state" widget="statusbar"/>
                </header>
                <sheet>
                    <group>
                        <group string="Propietario">
                            <field name="owner_name"/>
                            <field name="owner_email"/>
                            <field name="owner_phone"/>
                        </group>
                        <group string="Propiedad">
                            <field name="name"/>
                            <field name="property_type"/>
                            <field name="listing_type"/>
                            <field name="address"/>
                            <field name="zone"/>
                            <field name="bedrooms"/>
                            <field name="capacity"/>
                            <field name="price_per_night"/>
                        </group>
                    </group>
                    <field name="description"/>
                    <field name="amenities"/>
                    <group string="Fotos">
                        <field name="image_1" widget="image"/>
                        <field name="image_2" widget="image"/>
                        <field name="image_3" widget="image"/>
                    </group>
                    <field name="product_id" readonly="1"/>
                </sheet>
                <div class="oe_chatter">
                    <field name="message_follower_ids"/>
                    <field name="message_ids"/>
                </div>
            </form>
        </field>
    </record>

    <record id="action_property_submissions" model="ir.actions.act_window">
        <field name="name">Solicitudes de Captación</field>
        <field name="res_model">real.estate.property.submission</field>
        <field name="view_mode">list,form</field>
    </record>
</odoo>
```

### 4.5 Seguridad — `security/ir.model.access.csv`

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_re_submission_manager,real.estate.property.submission manager,model_real_estate_property_submission,base.group_user,1,1,1,1
access_re_submission_public,real.estate.property.submission public,model_real_estate_property_submission,,0,0,1,0
```


---

## ETAPA 5 — Sincronización iCal con Airbnb / Booking.com

**Complejidad:** Alta | **Tiempo estimado:** 5-8 días | **Dependencias:** Etapas 1, 2, 4

### Qué se desarrolla
- Modelo `real.estate.ical.sync` para almacenar URLs de calendarios externos por propiedad
- Cron job que importa eventos iCal de Airbnb/Booking y los bloquea en el calendario de Odoo
- Exportación del calendario de Odoo en formato iCal para que Airbnb/Booking puedan importarlo
- Detección de conflictos: si una fecha ya está bloqueada, no se puede reservar online

### Cómo funciona iCal con Airbnb y Booking
- **Airbnb** y **Booking.com** exponen una URL pública `.ics` con las reservas de cada propiedad
- Odoo importa esas URLs periódicamente y bloquea las fechas ocupadas
- Odoo también expone una URL `.ics` que Airbnb/Booking pueden importar para ver las reservas de Odoo
- Esto evita el doble booking entre plataformas

### 5.1 Dependencia Python
Agregar al servidor Odoo (o al `requirements.txt` del módulo):
```
icalendar>=5.0.0
```
Instalar en el entorno de Odoo: `pip install icalendar`

### 5.2 Modelo — `models/ical_sync.py`

```python
import logging
import requests
from datetime import datetime, date
from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    from icalendar import Calendar
    ICALENDAR_AVAILABLE = True
except ImportError:
    ICALENDAR_AVAILABLE = False
    _logger.warning("icalendar no instalado. Instalar con: pip install icalendar")


class ICalSync(models.Model):
    _name = 'real.estate.ical.sync'
    _description = 'Sincronización iCal de Propiedad'

    product_id = fields.Many2one(
        'product.template', string="Propiedad",
        required=True, ondelete='cascade',
        domain=[('rent_ok', '=', True)]
    )
    platform = fields.Selection([
        ('airbnb', 'Airbnb'),
        ('booking', 'Booking.com'),
        ('other', 'Otro'),
    ], string="Plataforma", required=True)
    ical_url = fields.Char(string="URL del Calendario (.ics)", required=True)
    last_sync = fields.Datetime(string="Última Sincronización", readonly=True)
    sync_status = fields.Char(string="Estado", readonly=True)
    blocked_line_ids = fields.One2many(
        'real.estate.blocked.period', 'sync_id', string="Períodos Bloqueados"
    )

    def action_sync_now(self):
        for sync in self:
            sync._do_sync()

    def _do_sync(self):
        self.ensure_one()
        if not ICALENDAR_AVAILABLE:
            raise UserError("Instalar la librería icalendar: pip install icalendar")
        try:
            response = requests.get(self.ical_url, timeout=15)
            response.raise_for_status()
            cal = Calendar.from_ical(response.content)

            # Eliminar períodos anteriores de esta sync
            self.blocked_line_ids.unlink()

            new_periods = []
            for component in cal.walk():
                if component.name != 'VEVENT':
                    continue
                dtstart = component.get('DTSTART')
                dtend = component.get('DTEND')
                if not dtstart or not dtend:
                    continue
                start = dtstart.dt
                end = dtend.dt
                if isinstance(start, datetime):
                    start = start.date()
                if isinstance(end, datetime):
                    end = end.date()
                summary = str(component.get('SUMMARY', 'Reserva externa'))
                new_periods.append({
                    'sync_id': self.id,
                    'product_id': self.product_id.id,
                    'date_start': start,
                    'date_end': end,
                    'summary': summary,
                })

            self.env['real.estate.blocked.period'].create(new_periods)
            self.write({
                'last_sync': fields.Datetime.now(),
                'sync_status': f'OK — {len(new_periods)} períodos importados',
            })
        except Exception as e:
            self.write({'sync_status': f'Error: {str(e)}'})
            _logger.exception("Error sincronizando iCal para %s: %s", self.product_id.name, e)

    @api.model
    def _cron_sync_all(self):
        """Llamado por el cron job para sincronizar todos los calendarios."""
        syncs = self.search([])
        for sync in syncs:
            sync._do_sync()


class BlockedPeriod(models.Model):
    _name = 'real.estate.blocked.period'
    _description = 'Período Bloqueado por Reserva Externa'

    sync_id = fields.Many2one('real.estate.ical.sync', ondelete='cascade')
    product_id = fields.Many2one('product.template', string="Propiedad", required=True)
    date_start = fields.Date(string="Desde", required=True)
    date_end = fields.Date(string="Hasta", required=True)
    summary = fields.Char(string="Descripción")

    def is_period_blocked(self, product_id, start_date, end_date):
        """Verificar si un período está bloqueado para una propiedad."""
        blocked = self.search([
            ('product_id', '=', product_id),
            ('date_start', '<', end_date),
            ('date_end', '>', start_date),
        ], limit=1)
        return bool(blocked)
```

### 5.3 Exportación iCal de Odoo — `controllers/ical_export.py`

```python
from odoo import http, fields
from odoo.http import request

class ICalExportController(http.Controller):

    @http.route('/ical/<int:product_id>/calendar.ics', type='http', auth='public')
    def export_ical(self, product_id, **kwargs):
        try:
            from icalendar import Calendar, Event
            from datetime import datetime
        except ImportError:
            return request.make_response('icalendar not installed', status=500)

        product = request.env['product.template'].sudo().browse(product_id)
        if not product.exists() or not product.rent_ok:
            return request.not_found()

        cal = Calendar()
        cal.add('prodid', '-//Real Estate Odoo//real_estate//ES')
        cal.add('version', '2.0')
        cal.add('x-wr-calname', product.name)

        # Buscar órdenes de venta confirmadas para esta propiedad
        order_lines = request.env['sale.order.line'].sudo().search([
            ('product_id.product_tmpl_id', '=', product_id),
            ('is_rental', '=', True),
            ('order_id.state', 'in', ['sale', 'done']),
            ('order_id.rental_start_date', '!=', False),
        ])

        for line in order_lines:
            event = Event()
            event.add('summary', f'Reservado — {line.order_id.partner_id.name}')
            event.add('dtstart', line.order_id.rental_start_date.date())
            event.add('dtend', line.order_id.rental_return_date.date())
            event.add('uid', f'odoo-rental-{line.id}@real_estate')
            cal.add_component(event)

        return request.make_response(
            cal.to_ical(),
            headers=[
                ('Content-Type', 'text/calendar; charset=utf-8'),
                ('Content-Disposition', f'attachment; filename="{product.name}.ics"'),
            ]
        )
```

### 5.4 Cron Job — `data/ical_cron.xml`

```xml
<odoo>
    <record id="ir_cron_ical_sync" model="ir.cron">
        <field name="name">Real Estate: Sincronizar Calendarios iCal</field>
        <field name="model_id" ref="model_real_estate_ical_sync"/>
        <field name="state">code</field>
        <field name="code">model._cron_sync_all()</field>
        <field name="interval_number">6</field>
        <field name="interval_type">hours</field>
        <field name="numbercall">-1</field>
        <field name="active" eval="True"/>
    </record>
</odoo>
```

### 5.5 Vista Backend — `views/ical_sync_views.xml`

```xml
<odoo>
    <record id="view_ical_sync_list" model="ir.ui.view">
        <field name="name">real.estate.ical.sync.list</field>
        <field name="model">real.estate.ical.sync</field>
        <field name="arch" type="xml">
            <list string="Sincronizaciones iCal">
                <field name="product_id"/>
                <field name="platform"/>
                <field name="last_sync"/>
                <field name="sync_status"/>
                <button name="action_sync_now" string="Sincronizar" type="object" icon="fa-refresh"/>
            </list>
        </field>
    </record>

    <record id="view_ical_sync_form" model="ir.ui.view">
        <field name="name">real.estate.ical.sync.form</field>
        <field name="model">real.estate.ical.sync</field>
        <field name="arch" type="xml">
            <form string="Sincronización iCal">
                <header>
                    <button name="action_sync_now" string="Sincronizar Ahora" type="object" class="btn-primary"/>
                </header>
                <sheet>
                    <group>
                        <field name="product_id"/>
                        <field name="platform"/>
                        <field name="ical_url" widget="url"/>
                        <field name="last_sync"/>
                        <field name="sync_status"/>
                    </group>
                    <field name="blocked_line_ids">
                        <list>
                            <field name="date_start"/>
                            <field name="date_end"/>
                            <field name="summary"/>
                        </list>
                    </field>
                </sheet>
            </form>
        </field>
    </record>

    <record id="action_ical_sync" model="ir.actions.act_window">
        <field name="name">Calendarios iCal</field>
        <field name="res_model">real.estate.ical.sync</field>
        <field name="view_mode">list,form</field>
    </record>
</odoo>
```

### 5.6 Cómo obtener la URL iCal de Airbnb y Booking

**Airbnb:**
1. Ir a Airbnb → Calendario de la propiedad → Disponibilidad
2. Buscar "Exportar calendario" → Copiar URL `.ics`
3. Pegar esa URL en Odoo → Real Estate → Calendarios iCal

**Booking.com:**
1. Ir a Booking.com Extranet → Propiedad → Calendario
2. Buscar "Sincronización de calendario" → "Exportar calendario"
3. Copiar URL `.ics` y pegar en Odoo

**URL de exportación de Odoo para Airbnb/Booking:**
- Formato: `https://tudominio.com/ical/<product_id>/calendar.ics`
- Esta URL se ingresa en Airbnb/Booking como "Importar calendario externo"

---

## RESUMEN DE ETAPAS Y ORDEN DE EJECUCIÓN

| Etapa | Descripción | Complejidad | Días est. | Prioridad |
|-------|-------------|-------------|-----------|-----------|
| 1 | WhatsApp flotante + redes sociales | Baja | 1-2 | Alta — base del módulo |
| 2 | Mapa Leaflet con filtro por zona | Media | 3-5 | Alta — diferenciador clave |
| 3 | Payment Provider Bold | Alta | 5-8 | Media — puede usar Stripe interim |
| 4 | Portal captación de propietarios | Alta | 5-7 | Media — importante para el negocio |
| 5 | Sync iCal Airbnb/Booking | Alta | 5-8 | Alta — evita doble booking |

**Orden recomendado de desarrollo:**
1. Etapa 1 (base del módulo, scaffolding)
2. Etapa 5 (iCal — crítico para operación)
3. Etapa 2 (mapa — diferenciador visual)
4. Etapa 4 (captación — generación de leads)
5. Etapa 3 (Bold — puede usar Stripe mientras tanto)

## ESTRUCTURA FINAL DEL MÓDULO `real_estate`

```
real_estate/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── res_config_settings.py       # Etapa 1
│   ├── product_template.py          # Etapa 2 (campos lat/lng/zona)
│   ├── property_submission.py       # Etapa 4
│   └── ical_sync.py                 # Etapa 5
├── controllers/
│   ├── __init__.py
│   ├── map.py                       # Etapa 2
│   ├── captacion.py                 # Etapa 4
│   └── ical_export.py               # Etapa 5
├── views/
│   ├── res_config_settings_views.xml
│   ├── product_template_views.xml
│   ├── property_submission_views.xml
│   ├── ical_sync_views.xml
│   └── menus.xml
├── templates/
│   ├── whatsapp_social.xml          # Etapa 1
│   ├── map_page.xml                 # Etapa 2
│   └── captacion.xml                # Etapa 4
├── data/
│   └── ical_cron.xml                # Etapa 5
├── security/
│   └── ir.model.access.csv
└── static/
    └── src/
        └── css/
            └── floating_buttons.css # Etapa 1

payment_bold/                        # Etapa 3 — módulo separado
├── __init__.py
├── __manifest__.py
├── const.py
├── models/
│   ├── payment_provider.py
│   └── payment_transaction.py
├── controllers/
│   └── main.py
├── views/
│   ├── payment_bold_templates.xml
│   ├── payment_form_templates.xml
│   └── payment_provider_views.xml
└── data/
    └── payment_provider_data.xml
```

> **Nota:** El módulo `payment_bold` se crea como módulo independiente (igual que `payment_stripe`, `payment_mercado_pago`) para seguir el patrón estándar de Odoo y facilitar el mantenimiento.
