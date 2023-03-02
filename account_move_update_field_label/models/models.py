# -*- coding: utf-8 -*-

from odoo import models,fields



class AccountMove(models.Model):
    _inherit = 'account.move'
    usuario_timbrado = fields.Many2one('res.users','Timbrado por')
    version_cfdi = fields.Char('Versión CFDI')

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


