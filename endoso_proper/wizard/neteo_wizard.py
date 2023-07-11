# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, fields, _
from odoo.exceptions import UserError, ValidationError
from lxml.objectify import fromstring
class EndosoWizard(models.TransientModel):
    _name = 'neteo.wizard'
    _description = 'Muestra un wizard para el proceso de neteo (Pago por compensación) de facturas'

    factura = fields.Many2one('account.move', string='Factura a endosar', help='Factura que se va a endosar' )
    cliente = fields.Many2one('res.partner', string='Cliente', help='Nombre del cliente al que se le va a endosar la factura')
    monto = fields.Float('Monto',help='Monto que se va a pagar por compensación')

    def done_neteo(self):
        if self:
            invoice = self.env['account.move'].search([('id', '=', self.factura.id)])
            cliente = self.cliente
            if not cliente:
                raise ValidationError('No se ha seleccionado un cliente')
            if not cliente.property_account_receivable_id.id:
                raise ValidationError('No se ha definido la cuenta por cobrar del cliente')
            journal = self.env['account.journal'].search([('name','ilike','endoso')])
            if not journal:
                raise ValidationError('No hay diario para llevar a cabo la operación Endoso')
            endoso_dict = {
                'journal_id': journal.id,
                'partner_id': self.cliente.id,
                'origin_partner_id': invoice.partner_id.id,
                # 'name': self.env['ir.sequence'].next_by_code('account.move.endoso') or _('New'),
                'origin_invoice': invoice.id,
                'amount': total_porcentaje,
                'posted_before': True,
            }
            endoso = self.env['endoso.move'].create(endoso_dict)
            if endoso:
                line_ids_list = [
                    {
                        'name': 'Endoso ' + invoice.partner_id.name,
                        'move_id': endoso.move_id.id,
                        'partner_id': invoice.partner_id.id,
                        'account_id': invoice.partner_id.property_account_receivable_id.id,
                        'credit': total_porcentaje,
                    },
                    {
                        'name': 'Endoso ' + cliente.name,
                        'move_id': endoso.move_id.id,
                        'partner_id': cliente.id,
                        'account_id': cliente.property_account_receivable_id.id,
                        'debit': total_porcentaje,
                    }
                ]
                lineas = self.env['account.move.line'].create(line_ids_list)
                endoso.action_post()
                invoice_msg = (
                                  "Se generó el endoso: <a href=# data-oe-model=endoso.move data-oe-id=%d>%s</a> a partir de esta factura") % (
                                  endoso.id, endoso.name)
                endoso_msg = (
                                 "Este endoso fue creado desde: <a href=# data-oe-model=account.move data-oe-id=%d>%s</a>") % (
                                 invoice.id, invoice.name)
                invoice.message_post(body=invoice_msg, type="notification")
                endoso.message_post(body=endoso_msg, type="notification")
                return {
                    'name': _('Endoso'),
                    'view_mode': 'form',
                    'view_id': self.env.ref('endoso_proper.endoso_form_view').id,
                    'res_model': 'endoso.move',
                    'type': 'ir.actions.act_window',
                    'nodestroy': True,
                    'res_id': endoso.id,
                    'target': 'current',
                }