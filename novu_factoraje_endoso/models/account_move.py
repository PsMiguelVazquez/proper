# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class AccountMove(models.Model):
    #ENDOSO
    _inherit = 'account.move'
    ocultar_endoso = fields.Boolean(string='Ocultar endoso',
                                    help='Oculta el botón Endosar factura si ya está endosada',
                                    compute='_compute_ocultar_endoso')
    es_endoso = fields.Boolean(string='Es endoso')
    #FACTORAJE
    factoring_amount = fields.Float('Monto por factoraje')
    balance_after_factoring = fields.Float(string='Restante', compute='_compute_balance_after_factoring')
    balance_after_compensate = fields.Float(string='Restante', compute='_compute_balance_after_compensate')
    rel_payment = fields.Many2one('account.payment')

    #ENDOSO
    def is_inbound(self, include_receipts=True):
        if 'END/' in self.name and self.es_endoso:
            return True
        return self.move_type in self.get_inbound_types(include_receipts)

    def _compute_ocultar_endoso(self):
        for record in self:
            if self.env['endoso.move'].search([('origin_invoice','=',record.id)]).filtered(lambda x: x.state != 'cancel')\
                    or self.amount_residual == 0.0 or not self.l10n_mx_edi_cfdi_uuid:
                record['ocultar_endoso'] = True
            else:
                record['ocultar_endoso'] = False

    def endosar_factura(self):
        w = self.env['endoso.wizard'].sudo().create({'factura': self.id})
        view = self.env.ref('endoso_proper.view_endoso_wizard_form')
        return {
            'name': _('Endosar Facturas'),
            'type': 'ir.actions.act_window',
            'res_model': 'endoso.wizard',
            'view_mode': 'form',
            'res_id': w.id,
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new'
        }


    #FACTORAJE
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
    @api.depends('porcent_assign')
    def _compute_balance_after_compensate(self):
        for record in self:
            record.balance_after_compensate = record.amount_residual - record.porcent_assign

    @api.onchange('factoring_amount')
    def on_balance_after_factoring(self):
        for record in self:
            if record.porcent_assign == 0.0:
                record.porcent_assign = record.balance_after_factoring

    #def action_register_payment(self):
    #   view = self.env.ref('account.view_account_payment_register_form')
    #    # return super(AccountMove, self).action_register_payment()
    #    return {
    #        'name': _('Register Payment'),
    #        'res_model': 'account.payment.register',
    #        'view_mode': 'form',
    #        'views': [(view.id, 'form')],
    #        'view_id': view.id,
    #        'context': {
    #            'active_model': 'account.move',
    #            'active_ids': self.ids,
    #        },
    #        'target': 'new',
    #        'type': 'ir.actions.act_window',
    #    }

    def view_compensate_wizard(self):
        active_ids = self._context.get('active_ids')
        facturas = self.env['account.move'].browse(active_ids)
        facturas.write({'porcent_assign': 0.0})
        if len(facturas.mapped('partner_id')) != 1:
            raise UserError('No se puede aplicar compensación a facturas de diferentes clientes.')

        w = self.env['account.payment.register'].with_context(active_model='account.move',
                                                              active_ids=active_ids).create({
            'amount': 0.0,
            'hide_button_payment_register': True,
            'partner_bills': facturas,
            'financial_factor': facturas[0].partner_id.id
        })
        view = self.env.ref('factoraje_financiero.account_payment_register_form_compensate')
        return {
            'name': _('Compensación'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment.register',
            'view_mode': 'form',
            'res_id': w.id,
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new'
        }



    def view_financial_factoring_wizard(self):
        active_ids = self._context.get('active_ids')
        facturas = self.env['account.move'].browse(active_ids)
        if len(facturas.filtered(lambda x: x.payment_state == 'not_paid')) != len(facturas):
            raise UserError('No se puede aplicar factoraje a facturas pagadas o pagadas parcialmente.')
        if len(facturas.mapped('partner_id')) != 1:
            raise UserError('No se puede aplicar factoraje a facturas de diferentes clientes.')
        # if len(facturas.mapped('partner_bank_id')) > 1:
        #     raise UserError('No se puede aplicar factoraje a facturas con diferentes bancos asociados.')
        for factura in facturas:
            if not factura.partner_bank_id:
                if len(self.env.company.bank_ids) < 1:
                    raise UserError('No se puede aplicar factoraje a facturas sin banco asociado.')
                if factura.move_type != 'out_invoice':
                    raise UserError('Solo se puede aplicar factoraje a facturas de clientes.')
                else:
                    factura.partner_bank_id = self.env.company.bank_ids[0].id

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


