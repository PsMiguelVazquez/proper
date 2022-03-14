# -*- coding: utf-8 -*-
# from odoo import http


# class StockRoute(http.Controller):
#     @http.route('/stock_route/stock_route/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/stock_route/stock_route/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('stock_route.listing', {
#             'root': '/stock_route/stock_route',
#             'objects': http.request.env['stock_route.stock_route'].search([]),
#         })

#     @http.route('/stock_route/stock_route/objects/<model("stock_route.stock_route"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('stock_route.object', {
#             'object': obj
#         })
