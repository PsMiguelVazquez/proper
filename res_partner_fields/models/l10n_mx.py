# -*- coding: utf-8 -*-

from odoo import models


class L10nMxEdiPayment(models.Model):
    _inherit = 'l10n_mx_edi.payment.method'

    def name_get(self):
        result = []
        for rec in self:
            if self.env.context.get('hide_code'):
                name = rec.name
            else:
                name = str(rec.code) + ' - ' + rec.name
            result.append((rec.id, name))
        return result
