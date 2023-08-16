# -*- coding: utf-8 -*-
# (C) 2018 Smile (<http://www.smile.fr>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import math

from odoo import api, fields, models
from odoo import tools
from odoo.tools import (
    float_repr, float_round, float_compare, float_is_zero, html_sanitize, human_size,
    pg_varchar, ustr, OrderedSet, pycompat, sql, date_utils, unique, IterableGenerator,
    image_process, merge_sequences,
)

class ResCurrency(models.Model):
    _inherit = 'res.currency'

    # display_rounding = fields.Float(
    #     'Display Rounding Factor', digits=(12, 6))
    # display_decimal_places = fields.Integer(
    #     compute='_get_display_decimal_places')
    #
    # @api.depends('rounding', 'display_rounding')
    # def _get_display_decimal_places(self):
    #     for record in self:
    #         if not record.display_rounding:
    #             record.display_decimal_places = record.decimal_places
    #         elif 0 < record.display_rounding < 1:
    #             record.display_decimal_places = \
    #                 int(math.ceil(math.log10(1 / record.display_rounding)))
    #         else:
    #             record.display_decimal_places = 0


    def round(self, amount):
        r = super(ResCurrency, self).round(amount)
        precision = self.env.company.display_digits
        self.ensure_one()
        return tools.float_round(amount, precision_digits=precision)
