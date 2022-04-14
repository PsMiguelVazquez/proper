# -*- coding: utf-8 -*-

from odoo import models, fields, api


class account_payment_proper(models.TransientModel):
    _inherit = 'account.payment.register'
    partner_bank_ref = fields.Many2one('res.partner.bank', string='Cuenta Bancaria Cliente')

    @api.onchange('partner_id')
    def deoman_banks(self):
        for record in self:
            domain = {}
            banks = record.partner_id.bank_ids.ids
            res = {'domain': {'partner_bank_ref': [['id', 'in', banks]]}}
            return res


