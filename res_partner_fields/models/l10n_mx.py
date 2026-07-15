# -*- coding: utf-8 -*-

from odoo import api, models


class L10nMxEdiPayment(models.Model):
    _inherit = 'l10n_mx_edi.payment.method'

    # MIGRACIÓN V19: `name_get()` fue removido del core; el equivalente es
    # sobreescribir `_compute_display_name`. Como el resultado depende del
    # contexto (`hide_code`), hace falta `@api.depends_context` además de
    # `@api.depends`; sin ella Odoo reutiliza el valor cacheado del primer
    # contexto con el que se computó, ignorando cambios posteriores de
    # `hide_code`.
    @api.depends('code', 'name')
    @api.depends_context('hide_code')
    def _compute_display_name(self):
        for rec in self:
            if self.env.context.get('hide_code'):
                rec.display_name = rec.name
            else:
                rec.display_name = str(rec.code) + ' - ' + rec.name
