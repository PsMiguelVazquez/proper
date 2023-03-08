# -*- coding: utf-8 -*-

from odoo import models


class L10nMxEdiPayment(models.Model):
    _inherit = 'l10n_mx_edi.payment.method'

    def name_get(self):
        result = []
        for rec in self:
            if self.env.context.get('show_code'):
                name = str(rec.code) + '- ' +rec.name
            else:
                name = rec.name
            result.append((rec.id,name))
        return result
