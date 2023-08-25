# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, fields, _, api
from odoo.exceptions import UserError, ValidationError
from lxml.objectify import fromstring
class ConsolidacionWizardPurchase(models.TransientModel):
    _name = 'consolidacion.compras.wizard'
    _description = 'Muestra un wizard para el proceso consolidar compras'
    partner_id = fields.Many2one('res.partner', string='Proveedor')
    purchase_orders = fields.Many2many('purchase.order', string='Órdenes de compra')
    purchase_order_lines = fields.Many2many( 'purchase.order.line',string='Líneas de la orden')
    wizard_lines = fields.Many2many('pwizard.line', string='Líneas')
    partner_ref = fields.Char(string='Referencia del proveedor')

    def create(self, vals_list):
        r = super(ConsolidacionWizardPurchase, self).create(vals_list)
        if r:
            r._compute_lines()
        return r

    def done_consolidar_compra(self):
        self.purchase_orders.state = 'consolidate'
        lines = []
        provider = self.partner_id
        origin = [x for x in self.purchase_orders.mapped('origin') if x]
        partner_ref = [x for x in self.purchase_orders.mapped('partner_ref') if x]
        for line in self.wizard_lines:
            if line.product_qty > 0:
                line_detail = (0, 0, {
                    'product_id': line.product_id.id,
                    'product_qty': line.product_qty,
                    'price_unit': line.price_unit,
                })
                lines.append(line_detail)
        purchase_order = self.env['purchase.order'].create({
            'partner_id': provider.id,
            'order_line': lines,
            'origin': ', '.join(origin),
            'partner_ref': self.partner_ref,
            'sale_ids':self.purchase_orders.mapped('sale_ids')
        })
        if purchase_order:
            purchase_order.write({'state': 'draft'})
            msg = (
                              "Se consolidó esta orden desde: " +
                              ", ".join([("<a href=# data-oe-model=purchase.order data-oe-id=%d>%s</a>")%(x.id, x.name)
                                        for x in self.purchase_orders]))
            purchase_order.message_post(body=msg, type="notification")
            msg2 = ("Esta orden forma parte de la consolidación: <a href=# data-oe-model=purchase.order data-oe-id=%d>%s</a>") % (
                                purchase_order.id, purchase_order.name)
            for order in self.purchase_orders:
                order.message_post(body=msg2, type="notification")


    def _compute_lines(self):
        for record in self:
            order_lines = self.purchase_order_lines
            lista_productos = []
            lista_productos_precios = [
                (
                    x.product_id,
                    x.price_unit
                )
                for x in order_lines
            ]
            '''
                Quita los repetidos
            '''
            lista_productos_precios = list(set(lista_productos_precios))
            for elem in lista_productos_precios:
                lineas_a_consolidar = order_lines.filtered(lambda y: y.product_id == elem[0] and  y.price_unit == elem[1])
                suma_costos = 0.0
                lista_productos.append({
                    'product_id': elem[0].id
                    , 'product_qty': lineas_a_consolidar.product_qty if len(lineas_a_consolidar)  == 1 else sum(lineas_a_consolidar.mapped('product_qty'))
                    , 'price_unit': elem[1]
                    , 'purchase_order_char': ', '.join(lineas_a_consolidar.filtered(lambda x: x.product_id == elem[0]).mapped('order_id.name'))
                    , 'sequence': 10
                    , 'wizard_id': record.id
                })
            lines = self.env['pwizard.line'].create(lista_productos)
            if lines:
                record['wizard_lines'] = lines
            else:
                record['wizard_lines'] = None

class ConsolidarCompraLine(models.TransientModel):
    _name = 'pwizard.line'
    _description = 'Líneas de la consolidación de compras'

    wizard_id = fields.Many2one('consolidacion.compras.wizard')
    sequence = fields.Integer(default=10)
    product_id = fields.Many2one('product.product', string='Producto')
    product_qty = fields.Float('Cantidad')
    price_unit = fields.Float('Precio')
    price_subtotal = fields.Float('Subtotal', compute='_compute_totals')
    price_total = fields.Float('Total', compute='_compute_totals')
    purchase_order_char = fields.Char('Órdenes')

    @api.depends('price_unit', 'product_qty')
    def _compute_totals(self):
        for record in self:
            record.price_subtotal = record.product_qty * record.price_unit
            record.price_total = record.price_subtotal * (1 + record.product_id.taxes_id.amount/100)

