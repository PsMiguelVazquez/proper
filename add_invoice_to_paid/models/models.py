# -*- coding: utf-8 -*-
import odoo.exceptions
from odoo import models, fields, api, _
import json
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    amount_rest = fields.Float(compute='get_invoices')

    def action_process_edi_web_services(self):
        endosos = self.get_endosos()

        for endoso in endosos:
            origin_invoice_documents = self.env['endoso.move'].search([('move_id','=',endoso.id)]).origin_invoice.edi_document_ids
            endoso.edi_document_ids =origin_invoice_documents
        r = self.move_id.action_process_edi_web_services()
        for endoso in endosos:
            origin_invoice = self.env['endoso.move'].search([('move_id','=',endoso.id)]).origin_invoice
            origin_invoice.edi_document_ids = endoso.edi_document_ids
        return r

    def action_retry_edi_documents_error(self):
        endosos = self.get_endosos()
        for endoso in endosos:
            origin_invoice_documents = self.env['endoso.move'].search(
                [('move_id', '=', endoso.id)]).origin_invoice.edi_document_ids
            endoso.edi_document_ids = origin_invoice_documents
        r =  super(AccountPayment, self).action_retry_edi_documents_error()
        for endoso in endosos:
            origin_invoice = self.env['endoso.move'].search([('move_id','=',endoso.id)]).origin_invoice
            origin_invoice.edi_document_ids = endoso.edi_document_ids
        return r



    def get_endosos(self):
        for record in self:
            endosos = self.env['account.move']
            pay_rec_lines = record.line_ids.filtered(
                lambda line: line.account_internal_type in ('receivable', 'payable'))
            for field1, field2 in (('debit', 'credit'), ('credit', 'debit')):
                for partial in pay_rec_lines[f'matched_{field1}_ids']:
                    invoice_line = partial[f'{field1}_move_id']
                    invoice = invoice_line.move_id
                    if 'END/' in invoice.name and invoice.es_endoso:
                        endosos |= invoice
            return endosos



    def get_invoices(self):
        for record in self:
            totals = 0.0
            total_pagado = 0.0
            # for move in record.reconciled_invoice_ids:
            #     data = json.loads(move.invoice_payments_widget)
            #     if data:
            #         for payment in data['content']:
            #             payments = self.env['account.payment'].browse(payment['account_payment_id'])
            #             if payments:
            #                 if payments.id == record.id:
            #                     totals += payment['amount']
            # record.amount_rest = record.amount - totals
            pay_rec_lines = record.line_ids.filtered(lambda line: line.account_internal_type in ('receivable', 'payable'))
            for field1, field2 in (('debit', 'credit'), ('credit', 'debit')):
                for partial in pay_rec_lines[f'matched_{field1}_ids']:
                    payment_line = partial[f'{field2}_move_id']
                    invoice_line = partial[f'{field1}_move_id']
                    invoice_amount = partial[f'{field1}_amount_currency']
                    exchange_move = invoice_line.full_reconcile_id.exchange_move_id
                    invoice = invoice_line.move_id
                    total_pagado += invoice_amount
            record.amount_rest = record.amount - total_pagado


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
        #raise UserError(f'check_sum {check_sum}')
        move_line = self.env['account.move.line'].search([('payment_id', '=', self.payment.id), ('balance', '<', 0)])
        _logger.error(f'move_line {move_line}')
        ###Redondea a dos decimales
        if round(check_sum,2) > self.amount_rest:
            raise odoo.exceptions.UserError("No se puede asignar mas del monto: "+str(self.amount_rest) + '. Intentando asignar ' + str(check_sum))
        else:
            if move_line:
                if len(self.invoices_ids) < 1 and 'END/' in self.invoices_ids.name and self.invoices_ids.es_endoso:
                    _logger.error('ENTRE 1')
                    move = self.invoices_ids
                    domain = [
                        ('parent_state', '=', 'posted'),
                        ('account_internal_type', 'in', ('receivable', 'payable')),
                        ('reconciled', '=', False),
                    ]
                    to_reconcile = move_line
                    amount = move.porcent_assign
                    end = self.env['endoso.move'].search([('move_id', '=', move.id)])
                    move.invoice_date = end.invoice_date
                    move.l10n_mx_edi_cfdi_request = 'on_invoice'
                    move.payment_reference = end.origin_invoice.name
                    movs_reconciled = move._get_reconciled_invoices_partials()
                    if movs_reconciled:
                        move._get_reconciled_invoices_partials()[0][2].remove_move_reconcile()
                    inv_line = end.origin_invoice.line_ids.filtered(
                        lambda x: x.account_id.internal_type == 'receivable')
                    inv_line.write({'account_id': move_line.account_id.id})
                    to_reconcile |= inv_line
                    to_reconcile.write({'account_id': end.origin_invoice.partner_id.property_account_receivable_id.id})
                    to_reconcile.with_context({'paid_amount': amount}).reconcile()
                    move.amount_residual = end.amount_residual
                    move.amount_residual_signed = end.amount_residual
                else:
                    _logger.error('ENTRE 2')
                    for move in self.invoices_ids:
                        _logger.error(f'move.name {move.name}')
                        if 'END/' in move.name and move.es_endoso:
                            '''
                                Conciliar las líneas del endoso con el pago
                            '''
                            amount = move.porcent_assign
                            end = self.env['endoso.move'].search([('move_id','=',move.id)])
                            move.invoice_date = end.invoice_date
                            move.l10n_mx_edi_cfdi_request = 'on_invoice'
                            move.payment_reference = end.origin_invoice.name
                            move.payment_id = self.payment.id
                            move.with_context({'paid_amount': amount}).js_assign_outstanding_line(move_line.id)
                            # end.amount_paid += amount
                            # end.amount_residual = end.amount - end.amount_paid
                            # move.amount_paid = end.amount_paid
                            move.amount_residual = end.amount_residual
                            move.amount_residual_signed = end.amount_residual
                            #move.payment_id = self.payment.id
                        else:
                            amount = move.porcent_assign
                            if self.env.company.currency_id == move.currency_id:
                                move.with_context({'paid_amount': amount, 'no_exchange_difference': True}).js_assign_outstanding_line(move_line.id)
                            else:
                                move.with_context({'paid_amount': amount}).js_assign_outstanding_line(move_line.id)
            else:
                raise odoo.exceptions.UserError("No hay asiento disponible para el movimiento")
        return True


