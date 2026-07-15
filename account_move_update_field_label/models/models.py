# -*- coding: utf-8 -*-

from odoo import api, models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'
    usuario_timbrado = fields.Many2one('res.users', 'Timbrado por')
    version_cfdi = fields.Char('Versión CFDI')
    codigo_uso_cfdi = fields.Char(string="Código Uso CFDi", compute='_compute_codigo_uso_cfdi', store=False)

    # MIGRACIÓN V19: el `@api.depends` faltaba en 15.0; sin él, un campo no
    # almacenado no se recalcula al cambiar `l10n_mx_edi_usage` (queda con
    # el valor cacheado obsoleto). Se agrega para que el compute sea
    # correcto, sin cambiar su lógica.
    @api.depends('l10n_mx_edi_usage')
    def _compute_codigo_uso_cfdi(self):
        for record in self:
            if record.l10n_mx_edi_usage:
                record.codigo_uso_cfdi = str(record.l10n_mx_edi_usage)
            else:
                record.codigo_uso_cfdi = ''

    def action_post(self):
        super(AccountMove, self).action_post()
        for move in self:
            move.usuario_timbrado = self.env.user
            # MIGRACIÓN V19: en 15.0 `version_cfdi` se llenaba con
            # `edi_web_services_to_process` (un campo técnico del viejo
            # framework genérico `account_edi`, que `l10n_mx_edi` usaba
            # entonces). En 19.0, `l10n_mx_edi` ya no depende de
            # `account_edi` en absoluto (arquitectura de timbrado propia,
            # ver `l10n_mx_edi.document`), por lo que ese campo ni siquiera
            # existe si `account_edi` no está instalado. Esa fuente de
            # datos ya no existe; `version_cfdi` deja de poblarse
            # automáticamente al publicar. El campo se conserva (editable
            # manualmente) por compatibilidad con datos históricos.
        return True

    def button_draft(self):
        super(AccountMove, self).button_draft()
        for move in self:
            move.usuario_timbrado = None
            move.version_cfdi = None
        return True
