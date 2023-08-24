# -*- coding: utf-8 -*-
from collections import defaultdict
from datetime import datetime

from odoo import models, fields, _, api
from odoo.exceptions import UserError, ValidationError
from lxml.objectify import fromstring
class FactoringWizard(models.TransientModel):
    _inherit = 'account.payment.register'
    _description = 'Muestra un wizard para el proceso de factoraje financiero'

    hide_fields_factoraje = fields.Boolean(default=True)
    financial_factor = fields.Many2one('res.partner', string='Factorante')
    factor_bill = fields.Many2one('account.move', string='Factura del factorante')
    amount_factor_bill = fields.Monetary('Monto factura', related='factor_bill.amount_residual')
    amount_residual_factor_bill = fields.Monetary('Monto restante factoraje', compute='get_factor_bill_amount')
    partner_bills = fields.Many2many(comodel_name='account.move')

    @api.depends('partner_bills','amount_factor_bill')
    def get_factor_bill_amount(self):
        for record in self:
            record.amount_residual_factor_bill = record.amount_factor_bill - sum(record.partner_bills.mapped('factoring_amount'))

    def create_neteo(self):
        for record in self:
            journal = self.env['account.journal'].search([('name','=','NETEO')])
            if not journal:
                raise UserError('No existe diario para llevar a cabo la operación')
            move = self.env['account.move'].create({
                'ref': _(', '.join(self.partner_bills.mapped(('name'))))
                , 'journal_id': journal.id
            })
            move_lines = record.partner_bills.mapped('line_ids').filtered(lambda x: x.account_id.user_type_id.type in ('payable', 'receivable') and x.partner_id == record.partner_bills.mapped('partner_id'))
            move_lines |= record.factor_bill.mapped('line_ids').filtered(lambda x: x.account_id.user_type_id.type in ('payable', 'receivable') and x.partner_id == record.financial_factor)
            move_lines_d = []
            for inv in record.partner_bills:
                move_line_vals = {
                    'credit': inv.factoring_amount,
                    "partner_id": inv.partner_id.id,
                    "name": inv.name,
                    "account_id": inv.partner_id.property_account_receivable_id.id,
                }
                move_lines_d.append((0, 0, move_line_vals))
            move_line_vals = {
                'debit': sum(record.partner_bills.mapped('factoring_amount')),
                "partner_id": record.financial_factor.id,
                "name": record.factor_bill.name,
                "account_id": record.financial_factor.property_account_payable_id.id,
            }
            move_lines_d.append((0, 0, move_line_vals))
            move.write({"line_ids": move_lines_d, 'l10n_mx_edi_payment_method_id': 12})
            move.action_post()
            for move_line in move.line_ids:
                to_reconcile = move_line + move_lines.filtered(
                    lambda x: x.account_id == move_line.account_id and x.move_id.name == move_line.name
                )
                to_reconcile.reconcile()
            return move

    @api.onchange('partner_bills')
    def on_change_partner_bills(self):
        '''
            Calcula el monto del pago cada que cambia el monto individual de cada factura de cliente
        '''
        for record in self:
            if not record.hide_fields_factoraje:
                record.amount = sum(record.partner_bills.mapped('porcent_assign'))

    def action_create_payments(self):
        if self.hide_fields_factoraje:
            super(FactoringWizard, self).action_create_payments()
        else:
            '''
                Validaciones
            '''
            if not self.financial_factor:
                raise UserError('No se ha definido un factorante.')
            if not self.factor_bill:
                raise UserError('No se ha definido la factura/gasto del factorante.')
            if round(self.amount_residual_factor_bill,2) != 0.00:
                raise UserError('No se ha aplicado completamente el monto del factoraje.')
            if round(sum(self.partner_bills.mapped('balance_after_factoring')),2) != 0.00:
                raise UserError('No se han pagado las facturas por completo.')
            if self.l10n_mx_edi_payment_method_id.id == 22:
                raise UserError('La forma de pago 99 - Por definir no está permitida.')
            '''
                Si es pago por factoraje el partner del pago pasa a ser el factor
            '''
            self.partner_id = self.financial_factor
            payments = super(FactoringWizard, self).action_create_payments()
            return payments
    def _create_payments(self):
        payments = super(FactoringWizard, self)._create_payments()
        '''
            Si es proceso de factoraje se crea el neteo, se publica y se postea 
            para marcar como pagadas/parcialmente pagadas/en proceso de pago las facturas de cliente y proveedor
        '''
        if not self.hide_fields_factoraje:
            neteo = self.create_neteo()
            neteo.rel_payment = payments
            neteo.payment_id = payments.id
        return payments

    def _reconcile_payments(self, to_process, edit_mode=False):
        '''
            Si las facturas del cliente son mas de una se concilia por el monto ingresado
            en el campo porcent_assign
        '''
        if len(self.partner_bills) > 1:
            domain = [
                ('parent_state', '=', 'posted'),
                ('account_internal_type', 'in', ('receivable', 'payable')),
                ('reconciled', '=', False),
            ]
            for vals in to_process:
                payment_lines = vals['payment'].line_ids.filtered_domain(domain)
                lines = vals['to_reconcile']
                for line in lines:
                    account = line.account_id
                    to_reconcile = ((payment_lines + line).filtered_domain([('reconciled', '=', False)]))
                    to_reconcile.with_context({'paid_amount': line.move_id.porcent_assign}).reconcile()
        else:
            super(FactoringWizard, self)._reconcile_payments(to_process, edit_mode=False)