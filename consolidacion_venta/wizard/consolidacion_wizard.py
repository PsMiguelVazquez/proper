# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, fields, _, api
from odoo.exceptions import UserError, ValidationError
from lxml.objectify import fromstring
class ConsolidacionWizard(models.Model):
    _name = 'consolidacion.wizard'
    _description = 'Muestra un wizard para el proceso consolidar líneas de pedido de ventas'
    lines = fields.Many2many('wizard.consolidation.line')
    sale_orders = fields.Many2many('sale.order', string='Pedidos')
    total = fields.Float(string='Total')
    subtotal = fields.Float(string='Subtotal')

    def _compute_lines(self):
        for record in self:
            order_lines = self.sale_orders.mapped('order_line')
            consolidacion_lines = []
            productos = order_lines.mapped('product_id')
            lista_productos = []
            for producto in productos:
                tot = 0.0
                cantidades_productos = order_lines.filtered(lambda x: x.product_id == producto).mapped('product_uom_qty')
                precios_unitarios = order_lines.filtered(lambda x: x.product_id == producto).mapped('price_unit')
                for i,c in enumerate(cantidades_productos):
                    tot += cantidades_productos[i] *  precios_unitarios[i]
                cantidad_productos = sum(cantidades_productos)
                precio_unitario_prom = tot / cantidad_productos
                sale_order_char = ', '.join(order_lines.filtered(lambda x: x.product_id == producto).mapped('order_id.name'))
                orden_compra = ', '.join(order_lines.filtered(lambda x: x.product_id == producto and x.order_id.x_studio_n_orden_de_compra).mapped('order_id.x_studio_n_orden_de_compra'))
                lista_productos.append({
                    'product_id': producto.id
                    , 'quantity': cantidad_productos
                    , 'price_unit': precio_unitario_prom
                    , 'orden_compra': orden_compra
                    , 'sale_order_char': sale_order_char
                    , 'sequence': 10
                    , 'wizard_id': record.id
                })

            # for line in order_lines:
            #     consolidacion_lines.append({
            #         'product_id': line.product_id.id
            #         , 'quantity': line.product_uom_qty
            #         , 'price_unit': line.price_unit
            #         , 'sequence': 10
            #         , 'wizard_id': record.id
            #         , 'sale_order':line.order_id.id
            #         , 'orden_compra': line.order_id.x_studio_n_orden_de_compra
            #     })

            lines = self.env['wizard.consolidation.line'].create(lista_productos)
            if lines:
                record['lines'] = lines
            print()

    def create(self, vals_list):
        r = super(ConsolidacionWizard, self).create(vals_list)
        if r:
            r._compute_lines()
        return r


    def done_consolidar(self):
        print(self)

class ConsolidacionWizardLine(models.Model):
    _name= 'wizard.consolidation.line'
    _description = 'Líneas a consolidar'
    sequence = fields.Integer(default=10)
    product_id = fields.Many2one('product.product', string='Producto')
    quantity = fields.Float(string='Cantidad')
    price_unit = fields.Float(string='Precio Unitario')
    wizard_id = fields.Many2one('consolidacion.wizard')
    sale_order = fields.Many2one('sale.order')
    sale_order_char = fields.Char(string='Órdenes de venta')
    orden_compra = fields.Char(string='Orden de compra')
    subtotal = fields.Float(string='Subtotal', compute='_compute_totals')
    taxes = fields.Float(string='Impuestos', compute='_compute_totals')
    total = fields.Float(string='Total', compute='_compute_totals')

    def _compute_totals(self):
        for record in self:
            record.subtotal = record.price_unit * record.quantity
            record.taxes = record.subtotal * 0.16
            record.total = record.subtotal + record.taxes