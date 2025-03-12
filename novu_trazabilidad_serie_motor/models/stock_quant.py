# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = 'stock.quant'
    
    engine_number = fields.Char(string="Numero de motor", store=True)
    use_engine_number = fields.Boolean( readonly=True)
