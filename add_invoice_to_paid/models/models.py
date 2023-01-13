# -*- coding: utf-8 -*-
import odoo.exceptions
from odoo import models, fields, api, _


class AccountPayment(models.Model):
    _inherit = 'account.payment'

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
    porcent_assign = fields.Float('Porcentaje')


class AccountPaymentWidget(models.TransientModel):
    _name = 'account.payment.wizard.ex'
    payment = fields.Many2one('account.payment')
    invoices_ids = fields.Many2many('account.move')
    partner_id = fields.Many2one('res.partner')

    def done(self):
        check_sum = sum(self.invoices_ids.mapped('porcent_assign'))
        move_line = self.env['account.move.line'].search([('payment_id', '=', self.payment.id), ('balance', '<', 0)])
        if check_sum > 100:
            return odoo.exceptions.UserError("No se puede asignar mas del 100%")
        else:
            if move_line:
                for move in self.invoices_ids:
                    amount = self.payment.amount * (move.porcent_assign/100)
                    r = move.with_context({'paid_amount': amount}).js_assign_outstanding_line(move_line.id)
            else:
                return odoo.exceptions.UserError("No hay asiento disponible para el movimiento")
        return True


