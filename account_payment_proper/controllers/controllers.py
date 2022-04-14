# -*- coding: utf-8 -*-
# from odoo import http


# class AccountPaymentProper(http.Controller):
#     @http.route('/account_payment_proper/account_payment_proper/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/account_payment_proper/account_payment_proper/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('account_payment_proper.listing', {
#             'root': '/account_payment_proper/account_payment_proper',
#             'objects': http.request.env['account_payment_proper.account_payment_proper'].search([]),
#         })

#     @http.route('/account_payment_proper/account_payment_proper/objects/<model("account_payment_proper.account_payment_proper"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('account_payment_proper.object', {
#             'object': obj
#         })
