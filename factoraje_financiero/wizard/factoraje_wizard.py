# -*- coding: utf-8 -*-
from collections import defaultdict
from datetime import datetime

from odoo import models, fields, _, api
from odoo.exceptions import UserError, ValidationError
from lxml.objectify import fromstring
class FactoringWizard(models.TransientModel):
    _name = 'factoraje.financiero.wizard'
    _description = 'Muestra un wizard para el proceso de factoraje financiero'

    partner_id = fields.Many2one('res.partner', string='Cliente')
    financial_factor = fields.Many2one('res.partner', string='Factorante')
    provider_bill = fields.Many2one('account.move', string='Factura del proveedor')
    amount_provider_bill = fields.Float(string='Monto restante de la factura', compute='compute_amount_provider_bill')
    journal = fields.Many2one('account.journal', string='Diario')
    currency = fields.Many2one('res.currency', string='Moneda')
    memo = fields.Char(string='Memo')
    amount_total = fields.Float(string='Monto del pago', compute='compute_totals')
    payment_method = fields.Many2one('l10n_mx_edi.payment.method')
    partner_bills = fields.Many2many(comodel_name='account.move', string='Facturas del cliente')
    payment_date = fields.Datetime('Fecha de pago')
    factoring_total = fields.Float(string='Total por factoraje', compute='compute_totals')
    bank_total = fields.Float(string='Pago')
    line_ids = fields.Many2many('account.move.line', compute='get_line_ids')

    @api.depends('partner_bills')
    def get_line_ids(self):
        for record in self:
            record.line_ids = self.env['account.move.line']

    @api.depends('partner_bills')
    def compute_totals(self):
        for record in self:
            record.factoring_total = sum(record.partner_bills.mapped('factoring_amount'))
            record.amount_total = record.factoring_total + record.bank_total


    @api.depends('provider_bill')
    def compute_amount_provider_bill(self):
        for record in self:
            record.amount_provider_bill = 0.0
            if record.provider_bill:
                record.amount_provider_bill = record.provider_bill.amount_residual


    def done_factoring(self):
        '''
            Crear pago por compensación, aplicando el monto del campo factoring_amount para cada factura de cliente partner_bills
        '''
        print(self)
        self._get_batches()
        '''
            Crear pago con el método de pago especificado en el wizard para cada factura aplicando el monto en el campo porcent_assign
        '''
        print(self)
        '''
            Ver si se puede obtener los datos de ambos pagos y unirlos en un solo xml para mandar a timbrarlo
        '''
        print(self)

    def _get_batches(self):
        ''' Group the account.move.line linked to the wizard together.
        Lines are grouped if they share 'partner_id','account_id','currency_id' & 'partner_type' and if
        0 or 1 partner_bank_id can be determined for the group.
        :return: A list of batches, each one containing:
            * payment_values:   A dictionary of payment values.
            * moves:        An account.move recordset.
        '''
        self.ensure_one()

        lines = self.line_ids._origin

        if len(lines.company_id) > 1:
            raise UserError(_("You can't create payments for entries belonging to different companies."))
        if not lines:
            raise UserError(_("You can't open the register payment wizard without at least one receivable/payable line."))

        batches = defaultdict(lambda: {'lines': self.env['account.move.line']})
        for line in lines:
            batch_key = self._get_line_batch_key(line)
            serialized_key = '-'.join(str(v) for v in batch_key.values())
            vals = batches[serialized_key]
            vals['payment_values'] = batch_key
            vals['lines'] += line

        # Compute 'payment_type'.
        for vals in batches.values():
            lines = vals['lines']
            balance = sum(lines.mapped('balance'))
            vals['payment_values']['payment_type'] = 'inbound' if balance > 0.0 else 'outbound'

        return list(batches.values())

    def _get_line_batch_key(self, line):
        ''' Turn the line passed as parameter to a dictionary defining on which way the lines
        will be grouped together.
        :return: A python dictionary.
        '''
        move = line.move_id

        partner_bank_account = self.env['res.partner.bank']
        if move.is_invoice(include_receipts=True):
            partner_bank_account = move.partner_bank_id._origin

        return {
            'partner_id': line.partner_id.id,
            'account_id': line.account_id.id,
            'currency_id': line.currency_id.id,
            'partner_bank_id': partner_bank_account.id,
            'partner_type': 'customer' if line.account_internal_type == 'receivable' else 'supplier',
        }


