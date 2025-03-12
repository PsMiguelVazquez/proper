# -*- coding: utf-8 -*-
from odoo import fields, models

class Product(models.Model):
    _inherit = "product.product"

    def action_open_quants(self):
        # Override to hide the `removal_date` column if not needed.
        if not any(product.use_engine_number for product in self):
            self = self.with_context(hide_removal_engine=True)
        return super().action_open_quants()


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    use_engine_number = fields.Boolean(string='Use Engine Number',
        help='Cuando esta activo, debera especificar el numero de Motor para el producto')