# -*- coding: utf-8 -*-
import base64

from odoo import models, fields, api


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    partner_bank_ref = fields.Many2one('res.partner.bank', string='Cuenta Bancaria Cliente')
    registered_payment_id = fields.Many2many('account.payment')

    @api.onchange('partner_id')
    def deoman_banks(self):
        for record in self:
            banks = record.partner_id.bank_ids.ids
            res = {'domain': {'partner_bank_ref': [['id', 'in', banks]]}}
            return res

    def _create_payments(self):
        res = super(AccountPaymentRegister, self)._create_payments()
        self.registered_payment_id = res.ids
        return res

    def action_create_payments(self):
        res = super(AccountPaymentRegister, self).action_create_payments()
        for payment in self.registered_payment_id:
            # MIGRACIÓN V19: `report_action._render(res_id)` (llamado sobre un
            # registro concreto de ir.actions.report) ya no existe con esa
            # firma; `_render` ahora es @api.model y exige el report_ref
            # explícito. Se usa `_render_qweb_pdf`, la forma moderna e
            # idiomática para obtener directamente los bytes del PDF.
            pdf_content, _report_type = self.env['ir.actions.report']._render_qweb_pdf(
                'account.action_report_payment_receipt', res_ids=payment.id
            )
            b64_pdf = base64.b64encode(pdf_content)
            attach_name = "Complemento de pago.pdf"
            attachment = self.env['ir.attachment'].create({
                'name': attach_name,
                'type': 'binary',
                'datas': b64_pdf,
                'res_model': 'account.move',
                'res_id': payment.move_id.id,
                'mimetype': 'application/pdf',
            })
        return res
