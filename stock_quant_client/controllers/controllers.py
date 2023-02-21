# -*- coding: utf-8 -*-
# from odoo import http


# class StockQuantClient(http.Controller):
#     @http.route('/stock_quant_client/stock_quant_client/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/stock_quant_client/stock_quant_client/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('stock_quant_client.listing', {
#             'root': '/stock_quant_client/stock_quant_client',
#             'objects': http.request.env['stock_quant_client.stock_quant_client'].search([]),
#         })

#     @http.route('/stock_quant_client/stock_quant_client/objects/<model("stock_quant_client.stock_quant_client"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('stock_quant_client.object', {
#             'object': obj
#         })
