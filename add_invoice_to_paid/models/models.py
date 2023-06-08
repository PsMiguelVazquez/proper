# -*- coding: utf-8 -*-
import odoo.exceptions
from odoo import models, fields, api, _
import json
from odoo.exceptions import UserError

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    amount_rest = fields.Float(compute='get_invoices')

    def action_process_edi_web_services(self):
        if self.amount_rest > 0.0:
            raise UserError('No se puede timbrar un pago que no está totalmente aplicado. Falta aplicar: $' +str(self.amount_rest))
        r = super(AccountPayment, self).action_process_edi_web_services()
        return r

    def get_invoices(self):
        for record in self:
            totals = 0
            for move in record.reconciled_invoice_ids:
                data = json.loads(move.invoice_payments_widget)
                if data:
                    for payment in data['content']:
                        payments = self.env['account.payment'].browse(payment['account_payment_id'])
                        if payments:
                            if payments.id == record.id:
                                totals += payment['amount']
            record.amount_rest = record.amount - totals


    def asign_invoices(self):
        w = self.env['account.payment.wizard.ex'].create({'payment': self.id, 'partner_id': self.partner_id.id})
        view = self.env.ref('add_invoice_to_paid.add_invoice_to_paid_list')
        return {
                'name': _('Asignar Facturas'),
                'type': 'ir.actions.act_window',
                'res_model': 'account.payment.wizard.ex',
                'view_mode': 'form',
                'res_id': w.id,
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new'
            }


class AccountMove(models.Model):
    _inherit = 'account.move'
    porcent_assign = fields.Float('Monto')


class AccountPaymentWidget(models.TransientModel):
    _name = 'account.payment.wizard.ex'
    payment = fields.Many2one('account.payment')
    invoices_ids = fields.Many2many('account.move')
    partner_id = fields.Many2one('res.partner')
    amount_rest = fields.Float(related='payment.amount_rest')
    amount_applied = fields.Float('Monto aplicado' , compute='_compute_amount_applied')

    @api.depends('invoices_ids')
    def _compute_amount_applied(self):
        for record in self:
            record.amount_applied = sum(record.invoices_ids.mapped('porcent_assign'))



    def done(self):
        check_sum = sum(self.invoices_ids.mapped('porcent_assign'))
        move_line = self.env['account.move.line'].search([('payment_id', '=', self.payment.id), ('balance', '<', 0)])
        ###Redondea a dos decimales
        if round(check_sum,2) > self.amount_rest:
            raise odoo.exceptions.UserError("No se puede asignar mas del monto: "+str(self.amount_rest) + '. Intentando asignar ' + str(check_sum))
        else:
            if move_line:
                for move in self.invoices_ids:
                    amount = move.porcent_assign
                    r = move.with_context({'paid_amount': amount}).js_assign_outstanding_line(move_line.id)
            else:
                raise odoo.exceptions.UserError("No hay asiento disponible para el movimiento")
        return True


