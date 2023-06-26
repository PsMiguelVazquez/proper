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
    porcentaje = fields.Float(string='Porcentaje',help='Porcentaje de la factura que se va a endosar', default='0.70')


    def done_endoso(self):
        if self:
            invoice = self.env['account.move'].search([('id', '=', self.factura.id)])
            cliente = self.env['account.move'].search([('id', '=', self.factura.partner_id.id)])
            # porcentaje = self.env['account.move'].search([('id', '=', )])
            print(self.porcentaje)
            total_porcentaje = round(self.porcentaje * invoice.amount_total,2)
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
                        'debit': total_porcentaje,
                    },
                    {
                        'name': 'Endoso',
                        'move_id': invoice_id.id,
                        'account_id': invoice.partner_id.property_account_receivable_id.id,
                        'credit': total_porcentaje,
                    }
                ]
                lineas = self.env['account.move.line'].create(line_ids_list)
                return {
                    'name': _('Customer Invoice'),
                    'view_mode': 'form',
                    'view_id': self.env.ref('account.view_move_form').id,
                    'res_model': 'account.move',
                    'context': "{'move_type':'out_invoice'}",
                    'type': 'ir.actions.act_window',
                    'nodestroy': True,
                    'res_id': invoice_id.id,
                    'target': 'current',
                    'line_ids': lineas
                }
