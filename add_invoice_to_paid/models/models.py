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

    # MIGRACIÓN V19: red de seguridad para el mismo fenómeno ya visto en
    # `studio_fields_v19` (ver `models/self_heal.py` ahí): esta vista
    # apareció con `active=False` en un build de pruebas sin causa
    # rastreable en el código, y al no depender de una comparación de
    # versión de módulo -que puede saltarse migraciones enteras si el
    # backup restaurado ya trae la versión "actual"-, `_register_hook()`
    # es lo único confiable para reafirmarla en cada arranque del
    # registro (cada reinicio de proceso, cada `-u`/`-i`), sin depender de
    # un cron (que además está desactivado en bases no productivas).
    def _register_hook(self):
        super()._register_hook()
        view = self.env.ref('add_invoice_to_paid.add_invoice_to_paid_inherit', raise_if_not_found=False)
        if view and not view.active:
            view.write({'active': True})

    # MIGRACIÓN V19: `action_process_edi_web_services()`/
    # `action_retry_edi_documents_error()` (overrides aquí) pertenecen al
    # módulo genérico `account_edi`, del que `l10n_mx_edi` ya NO depende en
    # 19.0 (arquitectura de timbrado propia vía `l10n_mx_edi.document`).
    # `account_edi` no está instalado en este stack, por lo que estos
    # métodos no existen para hacer `super()`, y `edi_document_ids` (tanto
    # en `account.move` como en `endoso.move`) tampoco existe (ver hallazgo
    # idéntico en `endoso_proper`/`account_move_proper`). Este workaround
    # -intercambiar temporalmente los `edi_document_ids` del endoso y de la
    # factura de origen antes/después de timbrar- ya no tiene sentido: la
    # base sobre la que operaba desapareció por completo. Se elimina.

    def get_endosos(self):
        for record in self:
            endosos = self.env['account.move']
            # MIGRACIÓN V19: `account.payment` no expone `line_ids`
            # directamente (no usa `_inherits` hacia `account.move`); hay
            # que pasar por `move_id.line_ids`. `account_internal_type` ->
            # `account_type`.
            pay_rec_lines = record.move_id.line_ids.filtered(
                lambda line: line.account_type in ('asset_receivable', 'liability_payable'))
            for field1, field2 in (('debit', 'credit'), ('credit', 'debit')):
                for partial in pay_rec_lines[f'matched_{field1}_ids']:
                    invoice_line = partial[f'{field1}_move_id']
                    invoice = invoice_line.move_id
                    if invoice.name and 'END/' in invoice.name and invoice.es_endoso:
                        endosos |= invoice
            return endosos

    def get_invoices(self):
        for record in self:
            totals = 0.0
            total_pagado = 0.0
            # MIGRACIÓN V19: `move_id.line_ids` (ver nota en `get_endosos`);
            # `account_internal_type` -> `account_type`.
            pay_rec_lines = record.move_id.line_ids.filtered(lambda line: line.account_type in ('asset_receivable', 'liability_payable'))
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
    _description = 'Asignación manual de facturas a un pago'
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
                if len(self.invoices_ids) < 1 and self.invoices_ids.name and 'END/' in self.invoices_ids.name and self.invoices_ids.es_endoso:
                    move = self.invoices_ids
                    # MIGRACIÓN V19: `account_internal_type` -> `account_type`.
                    domain = [
                        ('parent_state', '=', 'posted'),
                        ('account_type', 'in', ('asset_receivable', 'liability_payable')),
                        ('reconciled', '=', False),
                    ]
                    to_reconcile = move_line
                    amount = move.porcent_assign
                    end = self.env['endoso.move'].search([('move_id', '=', move.id)])
                    move.invoice_date = end.invoice_date
                    # MIGRACIÓN V19: `l10n_mx_edi_cfdi_request` fue
                    # eliminado por completo (ver `endoso_proper`); esta
                    # asignación se quita.
                    move.payment_reference = end.origin_invoice.name
                    movs_reconciled = move._get_reconciled_invoices_partials()
                    if movs_reconciled:
                        move._get_reconciled_invoices_partials()[0][2].remove_move_reconcile()
                    # MIGRACIÓN V19: `account_id.internal_type` -> `account_type`.
                    inv_line = end.origin_invoice.line_ids.filtered(
                        lambda x: x.account_id.account_type == 'asset_receivable')
                    inv_line.write({'account_id': move_line.account_id.id})
                    to_reconcile |= inv_line
                    to_reconcile.write({'account_id': end.origin_invoice.partner_id.property_account_receivable_id.id})
                    to_reconcile.with_context({'paid_amount': amount}).reconcile()
                    move.amount_residual = end.amount_residual
                    move.amount_residual_signed = end.amount_residual
                else:
                    for move in self.invoices_ids:
                        if move.name and 'END/' in move.name and move.es_endoso:
                            '''
                                Conciliar las líneas del endoso con el pago
                            '''
                            amount = move.porcent_assign
                            end = self.env['endoso.move'].search([('move_id','=',move.id)])
                            move.invoice_date = end.invoice_date
                            move.payment_reference = end.origin_invoice.name
                            move.with_context({'paid_amount': amount}).js_assign_outstanding_line(move_line.id)
                            move.amount_residual = end.amount_residual
                            move.amount_residual_signed = end.amount_residual
                        else:
                            amount = move.porcent_assign
                            if self.env.company.currency_id == move.currency_id:
                                move.with_context({'paid_amount': amount, 'no_exchange_difference': True}).js_assign_outstanding_line(move_line.id)
                            else:
                                move.with_context({'paid_amount': amount}).js_assign_outstanding_line(move_line.id)
            else:
                raise odoo.exceptions.UserError("No hay asiento disponible para el movimiento")
        return True
