# -*- coding: utf-8 -*-
from collections import defaultdict
from datetime import datetime

from odoo import models, fields, _, api
from odoo.exceptions import UserError, ValidationError
from lxml.objectify import fromstring
import logging
_logger = logging.getLogger(__name__)

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

    def create_neteo(self, es_neteo = False):
        
        for record in self:
            #_logger.error(f"record {record}") logger pruebas
            journal = self.env['account.journal'].search([('name','ilike','neteo')])
            if not journal:
                raise UserError('No existe diario para llevar a cabo la operación')
            move = self.env['account.move'].create({
                'ref': _(', '.join(self.partner_bills.mapped(('name'))))
                , 'journal_id': journal.id
            })
            move_lines = record.partner_bills.mapped('line_ids').filtered(lambda x: x.account_id.user_type_id.type in ('payable', 'receivable') and x.partner_id == record.partner_bills.mapped('partner_id'))
            if not es_neteo:
                move_lines |= record.factor_bill.mapped('line_ids').filtered(lambda x: x.account_id.user_type_id.type in ('payable', 'receivable') and x.partner_id == record.financial_factor)
            else:
                move_lines |= record.factor_bill.mapped('line_ids').filtered(lambda x: x.account_id.user_type_id.type in ('payable', 'receivable'))
                
            move_lines_d = []
            for inv in record.partner_bills:
                move_line_vals = {
                    'credit': inv.factoring_amount,
                    "partner_id": inv.partner_id.id,
                    "name": inv.name,
                    "account_id": inv.partner_id.property_account_receivable_id.id,
                }
                move_lines_d.append((0, 0, move_line_vals))
            if not es_neteo:
                factor_account_creditor = record.financial_factor.property_account_creditor
            else:
                factor_account_creditor = record.factor_bill.partner_id.property_account_creditor
                
            if factor_account_creditor:
                line_account_id = factor_account_creditor.id
            else:
                if not es_neteo:
                    line_account_id = record.financial_factor.property_account_payable_id.id
                else:
                    line_account_id = record.factor_bill.partner_id.property_account_payable_id.id
                    
            move_line_vals = {
                'debit': sum(record.partner_bills.mapped('factoring_amount')),
                "partner_id": record.factor_bill.partner_id.id, #cambie esto record.financial_factor.id,
                "name": record.factor_bill.name,
                "account_id": line_account_id,
            }
            move_lines_d.append((0, 0, move_line_vals))
            
            #Se agrega para validar si existe IVA en el gasto que compensa el endoso
            has_iva_taxes = [tax for tax in record.factor_bill.invoice_line_ids.mapped('tax_ids') if 'iva' in tax.tax_group_id.name.lower()]
            has_iva = bool(has_iva_taxes)            
            _logger.error(f"has_iva: {has_iva}")
            if has_iva:        
                iva_tax = has_iva_taxes[0]  # Tomamos el primer impuesto que cumple la condición
                _logger.error(f"iva_tax: {iva_tax}")
                iva_account_id = iva_tax.cash_basis_transition_account_id.id if iva_tax.cash_basis_transition_account_id else None
    
                #_logger.error(f"iva_account_id: {iva_account_id}")
                #cuenta_credit = [cuenta.id for cuenta in iva_tax.invoice_repartition_line_ids.mapped('account_id') if 'iva' in cuenta.name.lower()]
                #raise UserError(f'cuenta_credit: {cuenta_credit[0]}')
                #if cuenta_credit:
                if not sum(record.partner_bills.mapped('factoring_amount')) == record.factor_bill.amount_total:
                    tipo_iva = has_iva_taxes[0].amount / 100 if has_iva_taxes else 0.0
                    total_iva = sum(record.partner_bills.mapped('factoring_amount')) * tipo_iva
                else:
                    total_iva = record.factor_bill.amount_tax
                #raise UserError(f'total_iva: {total_iva}')
                move_line_vals = {
                    'credit': total_iva,
                    "partner_id": record.factor_bill.partner_id.id, #cambie esto record.financial_factor.id,
                    "name": iva_tax.name,
                    "account_id": 35323,
                }  
                _logger.error(f"move_line_vals: {move_line_vals}")
                move_lines_d.append((0, 0, move_line_vals))

                move_line_vals = {
                    'debit': total_iva,
                    "partner_id": record.factor_bill.partner_id.id, #cambie esto record.financial_factor.id,
                    "name": iva_tax.name,
                    "account_id": 15,
                }  
                _logger.error(f"move_line_vals: {move_line_vals}")
                move_lines_d.append((0, 0, move_line_vals))
                #cuentas = iva_tax.invoice_repartition_line_ids
            
            #raise UserError(f'move_lines_d: {move_lines_d}')
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
            return super(FactoringWizard, self).action_create_payments()
        else:
            '''
                Validaciones
            '''
            if not self.financial_factor:
                raise UserError('No se ha definido un factorante.')
            if not self.factor_bill:
                raise UserError('No se ha definido la factura/gasto del factorante.')
            # if round(self.amount_residual_factor_bill,2) != 0.00:
            #     raise UserError('No se ha aplicado completamente el monto del factoraje.')
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
            # neteo.payment_id = payments.id
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
            return super(FactoringWizard, self)._reconcile_payments(to_process, edit_mode=False)