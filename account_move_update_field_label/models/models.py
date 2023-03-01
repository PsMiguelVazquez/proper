# -*- coding: utf-8 -*-

from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'


    def _compute_tax_totals_json(self):
        res = super(AccountMove, self)._compute_tax_totals_json()
        # self.tax_totals_json =  self.tax_totals_json.replace('Importe libre de impuestos', 'Subtotal')
        return res

