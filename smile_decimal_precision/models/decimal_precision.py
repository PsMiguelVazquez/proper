# -*- coding: utf-8 -*-
# (C) 2018 Smile (<http://www.smile.fr>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class DecimalPrecision(models.Model):
    _inherit = 'res.company'

    display_digits = fields.Integer('Precision Digits', required=True, default=2)
