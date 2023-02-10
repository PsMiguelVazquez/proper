# -*- coding: utf-8 -*-
from odoo import http

# class Vehiculos(http.Controller):
#     @http.route('/vehiculos/vehiculos/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vehiculos/vehiculos/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('vehiculos.listing', {
#             'root': '/vehiculos/vehiculos',
#             'objects': http.request.env['vehiculos.vehiculos'].search([]),
#         })

#     @http.route('/vehiculos/vehiculos/objects/<model("vehiculos.vehiculos"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vehiculos.object', {
#             'object': obj
#         })