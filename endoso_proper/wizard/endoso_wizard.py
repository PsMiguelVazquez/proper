# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, fields, _
from odoo.exceptions import UserError, ValidationError
from lxml.objectify import fromstring
class EndosoWizard(models.TransientModel):
    _name = 'endoso.wizard'
    _description = 'Muestra un wizard para el proceso de endoso de facturas'

    factura = fields.Many2one('account.move', string='Factura a endosar', help='Factura que se va a endosar' )
    cliente = fields.Many2one('res.partner', string='Cliente', help='Nombre del cliente al que se le va a endosar la factura')
    porcentaje = fields.Float(string='Porcentaje',help='Porcentaje de la factura que se va a endosar', default='70')


    def done_endoso(self):
        if self:
            invoice = self.env['account.move'].search([('id', '=', self.factura.id)])
            # 'line_ids': [
            #     Command.create({
            #         'label': 'Due amount',
            #         'account_id': self._get_demo_account(
            #             'income',
            #             'account.data_account_type_revenue',
            #             self.env.company,
            #         ).id,
            #         'amount_type': 'regex',
            #         'amount_string': r'BRT: ([\d,]+)',
            #     }),
            invoice_dict = {
                'journal_id': 1,
                'partner_id': self.cliente.id,
                'sale_id': invoice.sale_id,
                'name': self.env['ir.sequence'].next_by_code('account.move.endoso')
            }
            invoice_id = self.env['account.move'].create(invoice_dict)
            if invoice_id:
                line_ids_list = [
                    {
                        'name': 'Endoso',
                        'move_id': invoice_id.id,
                        'account_id': invoice.partner_id.property_account_receivable_id.id,
                        'debit': 1000.0,
                    },
                    {
                        'name': 'Endoso',
                        'move_id': invoice_id.id,
                        'account_id': invoice.partner_id.property_account_receivable_id.id,
                        'credit': 1000.0,
                    }
                ]
                lineas = self.env['account.move.line'].create(line_ids_list)
                # self.env['account.move.line'].create({
                #     'name': _('Automatic Balancing Line'),
                #     'move_id': self.account_opening_move_id.id,
                #     'account_id': balancing_account.id,
                #     'debit': credit_diff,
                #     'credit': debit_diff,
                # })
                return {
                    'name': _('Customer Invoice'),
                    'view_mode': 'form',
                    'view_id': self.env.ref('account.view_move_form').id,
                    'res_model': 'account.move',
                    'context': "{'move_type':'out_invoice'}",
                    'type': 'ir.actions.act_window',
                    'nodestroy': True,
                    'res_id': invoice_id.id,
                    'target': 'current'
                }
