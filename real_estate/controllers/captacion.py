import base64

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
            'bedrooms': int(post.get('bedrooms') or 0),
            'capacity': int(post.get('capacity') or 0),
            'price_per_night': float(post.get('price_per_night') or 0),
            'description': post.get('description', ''),
            'amenities': post.get('amenities', ''),
        }

        for i in range(1, 4):
            img_file = request.httprequest.files.get(f'image_{i}')
            if img_file and img_file.filename:
                vals[f'image_{i}'] = base64.b64encode(img_file.read())

        request.env['real.estate.property.submission'].sudo().create(vals)
        return request.render('real_estate.captacion_thanks', {})
