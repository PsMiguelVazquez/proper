# -*- coding: utf-8 -*-
# from odoo import http


# class SalePurchaseConfirm(http.Controller):
#     @http.route('/sale_purchase_confirm/sale_purchase_confirm/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_purchase_confirm/sale_purchase_confirm/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_purchase_confirm.listing', {
#             'root': '/sale_purchase_confirm/sale_purchase_confirm',
#             'objects': http.request.env['sale_purchase_confirm.sale_purchase_confirm'].search([]),
#         })

#     @http.route('/sale_purchase_confirm/sale_purchase_confirm/objects/<model("sale_purchase_confirm.sale_purchase_confirm"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_purchase_confirm.object', {
#             'object': obj
#         })
