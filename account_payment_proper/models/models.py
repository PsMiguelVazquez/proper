# -*- coding: utf-8 -*-
import base64

from odoo import models, fields, api


class account_payment_proper(models.TransientModel):
    _inherit = 'account.payment.register'
    partner_bank_ref = fields.Many2one('res.partner.bank', string='Cuenta Bancaria Cliente')
    registered_payment_id = fields.Integer(store=False)

    @api.onchange('partner_id')
    def deoman_banks(self):
        for record in self:
            domain = {}
            banks = record.partner_id.bank_ids.ids
            res = {'domain': {'partner_bank_ref': [['id', 'in', banks]]}}
            return res

    def _create_payments(self):
        res = super(account_payment_proper,self)._create_payments()
        self.registered_payment_id = res.id
        return res

    def action_create_payments(self):
        res = super(account_payment_proper,self).action_create_payments()
        account_move_id = self.env['account.move'].search([('name','=',self.communication)])
        pdf = self.env.ref('account.action_report_payment_receipt')._render(self.registered_payment_id)
        b64_pdf = base64.b64encode(pdf[0])
        attach_name = "Complemento de pago.pdf"
        attachment = self.env['ir.attachment'].create({
            'name': attach_name,
            'type': 'binary',
            'datas': b64_pdf,
            'res_model': 'account.move',
            'res_id': account_move_id.id,
            'mimetype': 'application/pdf',
        })
        return res
