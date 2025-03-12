# -*- coding: utf-8 -*-

import datetime
import dateutil.parser as dparser
from re import findall as re_findall

from odoo import fields, models
from odoo.tools import get_lang


class StockMove(models.Model):
    _inherit = "stock.move"
    use_engine_number = fields.Boolean(
        string='Use Engine Number', related='product_id.use_engine_number')

    