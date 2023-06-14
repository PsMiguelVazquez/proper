# -*- coding: utf-8 -*-
from odoo import models, fields, api
from collections import defaultdict
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare, float_is_zero, float_round
from datetime import datetime, timedelta
from odoo.exceptions import UserError



class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        old_price_dic = {x.default_code: x.product_tmpl_id.standard_price for x in self.move_line_ids_without_package.product_id}
        r = super(StockPicking, self).button_validate()
        if r == True and self.picking_type_id.code == 'incoming':
            orden_compra = self.env['purchase.order'].search([('name', '=', self.origin)])

            #Si el origen de la entrada es una orden de compra
            if orden_compra:
                lineas_orden = orden_compra.order_line
                productos_orden = lineas_orden.mapped('product_id')
                on_hand_qty_dic = {}
                for producto in productos_orden:
                    qty_on_hand = sum(producto.stock_quant_ids.filtered(lambda x: x.location_id.id in (187, 115, 80, 97, 103, 121)).mapped('quantity'))
                    cantidad_comprada_hecha = self.move_line_ids_without_package.filtered(lambda y: y.product_id == producto).qty_done
                    on_hand_qty_dic.update({producto.default_code:qty_on_hand - cantidad_comprada_hecha})
                purchase_cost_dic = {x.product_id.default_code: x.price_unit for x in lineas_orden}
                done_qtys_dic = {x.product_id.default_code: x.qty_done for x in  self.move_line_ids_without_package}
                std_price_dic = {}
                for elem in old_price_dic:
                    std_price_dic.update({elem: round((on_hand_qty_dic[elem] * old_price_dic[elem] + purchase_cost_dic[elem]* done_qtys_dic[elem])
                                                /(on_hand_qty_dic[elem] + done_qtys_dic[elem]),2) })
                for elem2 in std_price_dic:
                    product = self.env['product.product'].search([('default_code','=',elem2)])
                    product.product_tmpl_id.write({'standard_price_on_stock': std_price_dic[elem2], 'standard_price': std_price_dic[elem2]})
                return r
        return r