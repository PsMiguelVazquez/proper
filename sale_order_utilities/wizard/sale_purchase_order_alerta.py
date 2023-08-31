# -*- coding: utf-8 -*-
from collections import defaultdict
from datetime import datetime

from odoo import models, fields, _, api
from odoo.exceptions import UserError, ValidationError
from lxml.objectify import fromstring
class SalePurchaseOrderAlerta(models.TransientModel):
    _name = 'sale.purchase.order.alerta'
    message_top = fields.Html()
    message_bottom = fields.Html()
    lines = fields.Many2many('sale.order.line')
    res_order_id = fields.Many2one('sale.order')


    def confirm(self):
        sale_id = self.res_order_id
        sale_id.order_line.filtered(lambda x: x.check_price_reduce).write({'price_reduce_solicit': True})
        sale_id.write({'solicito_validacion': True})
        lines_no_stock = sale_id.order_line.filtered(
            lambda x: (
                                  x.product_id.stock_quant_warehouse_zero + x.x_cantidad_disponible_compra - x.product_uom_qty) < 0)
        if lines_no_stock:
            sale_id.write({'state': 'sale_conf', 'solicitud_parcial': True})
            lines_no_stock.write({'x_validacion_precio': True})
        # self.env['sale.order'].browse(self.env.context.get('active_ids')).write({'state': 'sale_conf'})
        sale_id.order_line.order_id.update({'state': 'sale_conf'})
        mensaje = '<h3>Se solicita la reducción de precio de los siguientes productos</h3><table class="table" style="width: 100%"><thead>' \
                  '<tr style="width: 30% !important;"><th>Producto</th>' \
                  '<th style="width: 10%">Costo promedio</th>' \
                  '<th style="width: 10%">Precio unitario anterior</th>' \
                  '<th style="width: 10%">Margen anterior</th>' \
                  '<th style="width: 10%">Nuevo costo</th>' \
                  '<th style="width: 10%">Nuevo precio mínimo recomendado</th>' \
                  '<th style="width: 10%">Nuevo precio unitario</th>' \
                  '<th style="width: 10%">Nuevo margen</th>' \
                  '</tr></thead>' \
                  '<tbody>'
        for order_line in sale_id.order_line:
            if order_line.price_reduce_v > 0.0:
                margen = order_line.product_id.x_fabricante[
                    'x_studio_margen_' + str(
                        order_line.order_id.x_studio_nivel)] if order_line.product_id.x_fabricante else 12
                mensaje += '<tr><td>' + order_line.name + '</td><td>' \
                           + str(order_line.product_id.standard_price) + '</td><td>' \
                           + str(round(order_line.get_valor_minimo() + .5)) + '</td><td>' \
                           + str(margen) + '</td><td>' \
                           + str(order_line.x_studio_nuevo_costo) + '</td><td>' \
                           + str(round(order_line.x_studio_nuevo_costo / ((100 - margen) / 100))) + '</td><td>' \
                           + str(round(order_line.price_unit)) + '</td><td>' \
                           + str(round((1 - (
                            order_line.x_studio_nuevo_costo / order_line.price_unit)) * 100) if order_line.x_studio_nuevo_costo > 0 else order_line.x_utilidad_por) \
                           + '</td></tr>'
        mensaje += '</tbody></table>'
        if lines_no_stock:
            mensaje += '</tbody></table>'
            mensaje += '<h3>Los siguientes productos no tienen existencia o tienen existencia parcial y se solicita la aprobación de la orden parcial</h3><table class="table" style="width: 100%;margin-left: auto;margin-right: auto;"><thead>' \
                       '<tr><th>Producto</th>' \
                       '<th>Disponible en almacén 0</th>' \
                       '<th>Costo promedio</th>' \
                       '<th>Cantidad solicitada</th>' \
                       '<th>Cantidad faltante</th>' \
                       '</tr></thead>' \
                       '<tbody>'
            for order_line in lines_no_stock:
                margen = order_line.product_id.x_fabricante[
                    'x_studio_margen_' + str(
                        order_line.order_id.x_studio_nivel)] if order_line.product_id.x_fabricante else 12
                mensaje += '<tr><td>' + order_line.x_descripcion_corta + '</td><td>' \
                           + str(order_line.product_id.stock_quant_warehouse_zero) + '</td><td>' \
                           + str(order_line.product_id.standard_price) + '</td><td>' \
                           + str(order_line.product_uom_qty) + '</td><td>' \
                           + str(
                    order_line.product_uom_qty + order_line.x_cantidad_disponible_compra - order_line.product_id.stock_quant_warehouse_zero) + '</td></tr>'
        mensaje += '</tbody></table>'

        sale_id.message_post(body=mensaje, type="notification")