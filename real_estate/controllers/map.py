import json
from datetime import datetime

from odoo import http
from odoo.http import request

ATTR_TIPO         = 'Tipo de propiedad'
ATTR_HABITACIONES = 'Habitaciones'
ATTR_ZONA         = 'Ubicacion/Zona'

# IDs fijos de atributos (de la BD ecommerce)
ATTR_IDS = {
    'zona':         20,
    'habitaciones': 21,
    'tipo':         24,
}


def _build_qs(zone=None, tipo=None, hab=None):
    params = []
    if zone: params.append('zone=' + zone)
    if tipo: params.append('tipo=' + tipo)
    if hab:  params.append('habitaciones=' + hab)
    return ('?' + '&amp;'.join(params)) if params else ''


class RealEstateMapController(http.Controller):

    @http.route('/mapa', type='http', auth='public', website=True)
    def map_page(self, zone=None, tipo=None, habitaciones=None, **kwargs):
        AttrVal = request.env['product.attribute.value'].sudo()

        def get_attr_values(attr_id):
            vals = request.env['product.attribute.value'].sudo().search(
                [('attribute_id', '=', attr_id)], order='sequence,name')
            # name es jsonb — extraer string del idioma activo
            lang = request.env.lang or 'es_AR'
            result = []
            for v in vals:
                name = v.name
                if isinstance(name, dict):
                    name = name.get(lang) or name.get('en_US') or list(name.values())[0]
                if name:
                    result.append(str(name))
            return result

        return request.render('real_estate.map_page', {
            'zones':             get_attr_values(ATTR_IDS['zona']),
            'tipos':             get_attr_values(ATTR_IDS['tipo']),
            'habitaciones_opts': get_attr_values(ATTR_IDS['habitaciones']),
            'selected_zone':     zone,
            'selected_tipo':     tipo,
            'selected_hab':      habitaciones,
            '_qs':               _build_qs,
        })

    @http.route('/mapa/propiedades.json', type='http', auth='public', website=True)
    def map_properties_json(self, zone=None, tipo=None, habitaciones=None,
                            date_in=None, date_out=None, guests=None, **kwargs):
        domain = [
            '&',
            '|', ('rent_ok', '=', True), ('sale_ok', '=', True),
            '&', ('re_show_on_map', '=', True),
            '&', ('re_latitude', '!=', False),
            '&', ('re_longitude', '!=', False),
                 ('is_published', '=', True),
        ]

        def ids_con_atributo(attr_id, valores):
            """Devuelve IDs de productos que tengan AL MENOS UNO de los valores."""
            lang = request.env.lang or 'es_AR'
            all_vals = request.env['product.attribute.value'].sudo().search(
                [('attribute_id', '=', attr_id)])
            matched_val_ids = []
            for v in all_vals:
                name = v.name
                if isinstance(name, dict):
                    name = name.get(lang) or name.get('en_US') or ''
                if str(name) in valores:
                    matched_val_ids.append(v.id)
            if not matched_val_ids:
                return []
            lines = request.env['product.template.attribute.line'].sudo().search(
                [('attribute_id', '=', attr_id), ('value_ids', 'in', matched_val_ids)])
            return lines.mapped('product_tmpl_id').ids

        # Cada param puede venir como valores separados por |
        if zone:
            valores = [z.strip() for z in zone.split('|')]
            ids = ids_con_atributo(ATTR_IDS['zona'], valores)
            domain.append(('id', 'in', ids))

        if tipo:
            valores = [t.strip() for t in tipo.split('|')]
            ids = ids_con_atributo(ATTR_IDS['tipo'], valores)
            domain.append(('id', 'in', ids))

        if habitaciones:
            valores = [h.strip() for h in habitaciones.split('|')]
            ids = ids_con_atributo(ATTR_IDS['habitaciones'], valores)
            domain.append(('id', 'in', ids))

        products = request.env['product.template'].sudo().search(domain)

        # ── Filtro de disponibilidad por fechas ──
        # Solo aplica a propiedades de alquiler con stock almacenable
        # Igual que Airbnb: si no está disponible en esas fechas, no aparece
        if date_in and date_out:
            try:
                dt_in  = datetime.strptime(date_in,  '%Y-%m-%d')
                dt_out = datetime.strptime(date_out, '%Y-%m-%d')
                if dt_out > dt_in:
                    warehouse_id = request.website.warehouse_id.id if request.website else None
                    # Separar alquileres (verificar disponibilidad) de ventas (siempre mostrar)
                    rental_products = products.filtered('rent_ok')
                    sale_only = products.filtered(lambda p: p.sale_ok and not p.rent_ok)
                    # Usar el método nativo de website_sale_stock_renting si está disponible
                    if hasattr(rental_products, '_filter_on_available_rental_products'):
                        available_rentals = rental_products._filter_on_available_rental_products(
                            dt_in, dt_out, warehouse_id
                        )
                    else:
                        available_rentals = rental_products
                    products = available_rentals | sale_only
            except (ValueError, TypeError):
                pass  # fechas inválidas → mostrar todo
        data = []
        for p in products:
            try:
                lat = float(p.re_latitude)
                lng = float(p.re_longitude)
            except (ValueError, TypeError):
                continue

            lang = request.env.lang or 'es_AR'
            attrs = {}
            for line in p.attribute_line_ids:
                vals_str = []
                for v in line.value_ids:
                    name = v.name
                    if isinstance(name, dict):
                        name = name.get(lang) or name.get('en_US') or ''
                    vals_str.append(str(name))
                attrs[line.attribute_id.id] = ', '.join(vals_str)

            price = None
            currency = ''
            if p.product_pricing_ids:
                min_p = min(p.product_pricing_ids, key=lambda x: x.price)
                price = float(min_p.price)
                currency = min_p.currency_id.symbol or min_p.currency_id.name

            data.append({
                'id':           p.id,
                'name':         p.name,
                'lat':          lat,
                'lng':          lng,
                'zone':         p.re_zone or '',
                'address':      p.re_address or '',
                'url':          '/shop/%s' % request.env['ir.http']._slug(p),
                'image_url':    '/web/image/product.template/%d/image_512' % p.id,
                'price':        price,
                'currency':     currency,
                'habitaciones': attrs.get(ATTR_IDS['habitaciones'], ''),
                'tipo':         attrs.get(ATTR_IDS['tipo'], ''),
                'rent_ok':      p.rent_ok,
                'sale_ok':      p.sale_ok,
            })

        return request.make_response(
            json.dumps(data),
            headers=[('Content-Type', 'application/json')],
        )
