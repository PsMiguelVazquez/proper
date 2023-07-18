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

    def _compute_lines(self):
        for record in self:
            order_lines = self.sale_orders.mapped('order_line')
            consolidacion_lines = []
            for line in order_lines:
                consolidacion_lines.append({
                    'product_id': line.product_id.id
                    , 'quantity': line.product_uom_qty
                    , 'price_unit': line.price_unit
                    , 'sequence': 10
                    , 'wizard_id': record.id
                })

            lines = self.env['wizard.consolidation.line'].create(consolidacion_lines)
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

