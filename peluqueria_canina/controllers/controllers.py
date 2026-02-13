# -*- coding: utf-8 -*-
# from odoo import http


# class PeluqueriaCanina(http.Controller):
#     @http.route('/peluqueria_canina/peluqueria_canina', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/peluqueria_canina/peluqueria_canina/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('peluqueria_canina.listing', {
#             'root': '/peluqueria_canina/peluqueria_canina',
#             'objects': http.request.env['peluqueria_canina.peluqueria_canina'].search([]),
#         })

#     @http.route('/peluqueria_canina/peluqueria_canina/objects/<model("peluqueria_canina.peluqueria_canina"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('peluqueria_canina.object', {
#             'object': obj
#         })

