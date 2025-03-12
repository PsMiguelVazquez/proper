# -*- coding: utf-8 -*-
import datetime
from odoo import api, fields, models, SUPERUSER_ID, _


class StockProductionLot(models.Model):
    #_inherit = 'stock.lot'
    _inherit = 'stock.production.lot'

    use_engine_number = fields.Boolean(
        string='Use Engine Number', related='product_id.use_engine_number', required=True)
    engine_number = fields.Char(string='Número de motor', store=True, readonly=False,
        help='Este es el numero de motor relacionado al numero de serie.')