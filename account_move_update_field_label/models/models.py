# -*- coding: utf-8 -*-

from odoo import models,fields



class AccountMove(models.Model):
    _inherit = 'account.move'
    usuario_timbrado = fields.Many2one('res.users','Timbrado por')
    version_cfdi = fields.Char('Versión CFDI')
    codigo_uso_cfdi = fields.Char(string="Código Uso CFDi",compute='_compute_codigo_uso_cfdi', store=False)


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
            move.version_cfdi = move.edi_web_services_to_process
        return True

    def button_draft(self):
        super(AccountMove, self).button_draft()
        for move in self:
            move.usuario_timbrado = None
            move.version_cfdi = None
        return True


