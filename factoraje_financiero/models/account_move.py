
from odoo import fields,models, _, api
from datetime import datetime
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'
    factoring_amount = fields.Float('Monto por factoraje')
    balance_after_factoring = fields.Float(string='Restante', compute='_compute_balance_after_factoring')
    rel_payment = fields.Many2one('account.payment')

    def write(self, vals):
        '''
            SI EL DIARIO ES EL CORRESPONDIENTE AL DE GASTOS Y EL MOVIMIENTO ESTÁ EN ESTADO BORRADOR
            CAMBIA LA CUENTA DE LA LÍNEA CONTABLE DE LA CUENTA DE PROVEEDOR A LA CUENTA DE ACREEDOR
            SI LA TIENE CONFIGURADA. SI NO NO HACE NINGÚN CAMBIO. (EL JOURNAL_ID ESTÁ HARDCODEADO.
            INTENTAR HACERLO GENÉRICO)
        '''
        def_journal = self._context.get('default_journal_id')
        if def_journal == 21 and self.state == 'draft':
            account_creditor = self.partner_id.property_account_creditor
            account_payable = self.partner_id.property_account_payable_id
            creditor_line = self.line_ids.filtered(lambda x: x.account_id == account_payable)
            if creditor_line:
                if account_creditor:
                    creditor_line.write({'account_id': account_creditor.id})
        return super(AccountMove, self).write(vals)

    @api.depends('porcent_assign', 'factoring_amount')
    def _compute_balance_after_factoring(self):
        for record in self:
            record.balance_after_factoring = record.amount_residual - record.factoring_amount - record.porcent_assign

    @api.onchange('factoring_amount')
    def on_balance_after_factoring(self):
        for record in self:
            if record.porcent_assign == 0.0:
                record.porcent_assign = record.balance_after_factoring



    def view_financial_factoring_wizard(self):
        active_ids = self._context.get('active_ids')
        facturas = self.env['account.move'].browse(active_ids)
        if len(facturas.filtered(lambda x: x.payment_state == 'not_paid')) != len(facturas):
            raise UserError('No se puede aplicar factoraje a facturas pagadas o pagadas parcialmente.')
        if len(facturas.mapped('partner_id')) != 1:
            raise UserError('No se puede aplicar factoraje a facturas de diferentes clientes.')

        facturas.write({'factoring_amount': 0.0, 'porcent_assign': 0.0})
        w = self.env['account.payment.register'].with_context(active_model='account.move', active_ids=active_ids).create({
            'group_payment': True,
            'hide_fields_factoraje': False,
            'partner_bills': facturas,
            'amount': 0.0
        })
        view = self.env.ref('factoraje_financiero.account_payment_register_form_factoring')
        return {
            'name': _('Factoraje'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment.register',
            'view_mode': 'form',
            'res_id': w.id,
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new'
        }