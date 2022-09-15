# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
from .. import extensions
from odoo.exceptions import UserError


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    origin = fields.Char(related='move_id.origin', string='Source', store=True)