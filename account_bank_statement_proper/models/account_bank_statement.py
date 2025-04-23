import base64

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    def validate_account_bank_statement(self, bank_statement, payments):
        """
        Valida que los pagos no estén duplicados en otros estados de cuenta
        y que el diario del pago coincida con el diario del estado de cuenta.
        """
        valid = True
        message = ''
        bank_statement_journal_id = bank_statement.journal_id.id

        # Obtiene las líneas de otros estados de cuenta
        estados_bancarios = self.env['account.bank.statement'].search([('id', '!=', bank_statement.id)])
        lineas_estados = estados_bancarios.mapped('line_ids')

        # Validación de pagos
        for payment in payments:
            for linea in lineas_estados:
                if linea.rel_payment.move_id.id == payment.id:
                    valid = False
                    message += f'\nEl pago {payment.name} ya está registrado en otro estado de cuenta con referencia: {linea.statement_id.name}'
                    break
            if payment.journal_id.id != bank_statement_journal_id:
                valid = False
                message += f'\nNo coincide el diario para el pago {payment.name}'
        return valid, message

    @api.model
    def create(self, values):
        """
        Sobrescribe el método create para validar los pagos al crear un estado de cuenta.
        """
        res = super(AccountBankStatement, self).create(values)
        line_payment_ids = res.line_ids.rel_payment.mapped('move_id')
        valid, message = self.validate_account_bank_statement(res, line_payment_ids)
        if not valid:
            raise UserError(message)
        return res

    def write(self, values):
        """
        Sobrescribe el método write para validar los pagos al actualizar un estado de cuenta.
        """
        res = super(AccountBankStatement, self).write(values)
        valid = True
        message = ''
        for bank_statement in self:
            line_payment_ids = bank_statement.line_ids.rel_payment.mapped('move_id')
            valid, _message = self.validate_account_bank_statement(bank_statement, line_payment_ids)
            if not valid:
                message += _message
        if not valid:
            raise UserError(message)
        return res

    @api.onchange('line_ids')
    def on_change_statement_lines(self):
        """
        Actualiza el balance final real y genera un nombre para el estado de cuenta
        basado en las facturas relacionadas.
        """
        self.balance_end_real = self.balance_end
        if not self.name or self.name == '':
            if self.line_ids:
                self.name = ','.join(self.line_ids[0].rel_payment.reconciled_invoice_ids.mapped('name'))
            else:
                self.name = ''


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    rel_payment = fields.Many2one('account.payment', string='Pago')
    rel_invoices_names = fields.Char('Facturas relacionadas')

    @api.onchange('rel_payment')
    def on_change_payment_id(self):
        """
        Actualiza los campos de la línea del estado de cuenta con los datos del pago relacionado.
        """
        for record in self:
            if record.rel_payment:
                referencia = ''
                record.l10n_mx_edi_payment_method_id = record.rel_payment.l10n_mx_edi_payment_method_id
                record.amount = record.rel_payment.amount if record.rel_payment.amount else 0.0
                record.partner_id = record.rel_payment.partner_id
                record.date = record.rel_payment.date
                record.statement_id.date = record.rel_payment.date
                for invoice in record.rel_payment.reconciled_invoice_ids:
                    referencia += invoice.name + ' '
                record.rel_invoices_names = referencia

    @api.constrains('rel_payment')
    def _check_lineas(self):
        """
        Valida que no existan pagos duplicados en las líneas del estado de cuenta.
        """
        for record in self:
            other_lines = record.statement_id.line_ids.filtered(lambda x: x.id != record.id)
            for line in other_lines:
                if line.rel_payment.name == record.rel_payment.name:
                    raise ValidationError("Existen pagos repetidos en las líneas del estado de cuenta")