from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSalePVC(WebsiteSale):
    
    @http.route()
    def shop(self, page=0, category=None, search='', min_price=0.0, max_price=0.0, ppg=False, **post):
        # Llamar al método original
        response = super().shop(page=page, category=category, search=search, 
                               min_price=min_price, max_price=max_price, ppg=ppg, **post)
        
        # Agregar series al contexto
        series = request.env['product.series'].sudo().search([('active', '=', True)], order='sequence')
        
        # Obtener filtros seleccionados
        selected_series = post.get('series_id')
        selected_glass = post.get('glass_type')
        
        # Aplicar filtros si existen
        domain = response.qcontext.get('search_product_domain', [])
        
        if selected_series:
            domain.append(('series_id', '=', int(selected_series)))
        
        if selected_glass:
            domain.append(('glass_type', '=', selected_glass))
        
        # Buscar productos con el dominio actualizado
        if selected_series or selected_glass:
            Product = request.env['product.template'].with_context(bin_size=True)
            products = Product.search(
                domain,
                limit=ppg if ppg else 20,
                offset=page * (ppg if ppg else 20),
                order=response.qcontext.get('search_order', 'website_sequence desc')
            )
            response.qcontext['products'] = products
            response.qcontext['search_count'] = Product.search_count(domain)
        
        # Agregar datos al contexto para los filtros
        response.qcontext.update({
            'pvc_series': series,
            'selected_series': selected_series,
            'selected_glass': selected_glass,
            'glass_types': [
                ('simple', 'Simple'),
                ('double', 'Doble'),
                ('triple', 'Triple'),
                ('low_e', 'Bajo Emisivo'),
            ],
        })
        
        return response
