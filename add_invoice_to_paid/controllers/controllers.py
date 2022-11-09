# -*- coding: utf-8 -*-
# from odoo import http


# class AddInvoiceToPaid(http.Controller):
#     @http.route('/add_invoice_to_paid/add_invoice_to_paid/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/add_invoice_to_paid/add_invoice_to_paid/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('add_invoice_to_paid.listing', {
#             'root': '/add_invoice_to_paid/add_invoice_to_paid',
#             'objects': http.request.env['add_invoice_to_paid.add_invoice_to_paid'].search([]),
#         })

#     @http.route('/add_invoice_to_paid/add_invoice_to_paid/objects/<model("add_invoice_to_paid.add_invoice_to_paid"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('add_invoice_to_paid.object', {
#             'object': obj
#         })
