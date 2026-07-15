# -*- coding: utf-8 -*-
# (C) 2018 Smile (<http://www.smile.fr>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, tools


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    def round(self, amount):
        super().round(amount)
        self.ensure_one()
        precision = self.env.company.display_digits
        return tools.float_round(amount, precision_digits=precision)
