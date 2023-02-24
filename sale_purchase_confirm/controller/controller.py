# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.tools.translate import _


class SaleRating(http.Controller):

    @http.route('/unreserved/<int:move>/<int:sale>', type='http', auth="public", website=True)
    def open_rate(self, move,sale, **kwargs):
        move = request.env['stock.move.line'].sudo().search([['id', '=', move]])
        sale_ob = request.env['sale.order'].sudo().search([['id', '=', sale]])
        if sale_ob.user_id.id == request.session.uid:
            move.move_id._do_unreserve()
        action_id = request.env.ref('sale.action_orders')
        return request.redirect("/web#id="+str(sale)+"&cids=1&menu_id=217&action="+str(action_id.id)+"&model=sale.order&view_type=form")


