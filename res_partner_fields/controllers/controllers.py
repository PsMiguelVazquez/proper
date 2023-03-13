# -*- coding: utf-8 -*-
# from odoo import http


# class ResPartnerFields(http.Controller):
#     @http.route('/res_partner_fields/res_partner_fields', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/res_partner_fields/res_partner_fields/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('res_partner_fields.listing', {
#             'root': '/res_partner_fields/res_partner_fields',
#             'objects': http.request.env['res_partner_fields.res_partner_fields'].search([]),
#         })

#     @http.route('/res_partner_fields/res_partner_fields/objects/<model("res_partner_fields.res_partner_fields"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('res_partner_fields.object', {
#             'object': obj
#         })
