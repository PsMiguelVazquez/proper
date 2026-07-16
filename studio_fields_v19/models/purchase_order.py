# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    x_studio_costo_total = fields.Float(
        string='Importe entregado', compute='_compute_x_studio_costo_total', store=True)

    @api.depends('price_unit', 'qty_received')
    def _compute_x_studio_costo_total(self):
        for record in self:
            record.x_studio_costo_total = record.qty_received * record.price_unit


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    x_suma_costo_total = fields.Float(
        string='Suma', compute='_compute_x_suma_costo_total', store=True)

    @api.depends('order_line.x_studio_costo_total')
    def _compute_x_suma_costo_total(self):
        for record in self:
            record.x_suma_costo_total = sum(record.order_line.mapped('x_studio_costo_total'))
