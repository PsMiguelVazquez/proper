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
    porcentaje = fields.Float(string='Porcentaje',help='Porcentaje de la factura que se va a endosar', default='1')


    def done_endoso(self):
        if self:
            invoice = self.env['account.move'].search([('id', '=', self.factura.id)])
            cliente = self.cliente
            if not cliente:
                raise ValidationError('No se ha seleccionado un cliente')
            if not cliente.property_account_receivable_id.id:
                raise ValidationError('No se ha definido la cuenta por cobrar del cliente')
            if invoice.partner_id == cliente:
                raise ValidationError('No se puede endosar una factura al mismo cliente')
            if self.porcentaje > 1:
                raise ValidationError('Valor inválido para el porcentaje. El valor máximo es 100')
            if self.porcentaje <=0.0:
                raise ValidationError('Valor inválido para el porcentaje. El porcentaje de endoso debe ser mayor a 0')
            total_porcentaje = round(self.porcentaje * invoice.amount_total,2)
            endoso_dict = {
                'journal_id': 1,
                'partner_id': self.cliente.id,
                'sale_id': invoice.sale_id,
                'cliente_endoso': invoice.partner_id.id,
                'name': self.env['ir.sequence'].next_by_code('account.move.endoso'),
                'factura_endosada': invoice.id,
                'es_endoso': True
            }
            endoso = self.env['account.move'].create(endoso_dict)
            invoice_msg = (
                              "Se generó el endoso: <a href=# data-oe-model=account.move data-oe-id=%d>%s</a> a partir de esta factura") % (
                              endoso.id, endoso.name)
            endoso_msg = (
                              "Este endoso fue creado desde: <a href=# data-oe-model=account.move data-oe-id=%d>%s</a>") % (
                              invoice.id, invoice.name)
            invoice.message_post(body=invoice_msg, type="notification")
            endoso.message_post(body=endoso_msg, type="notification")
            if endoso:
                line_ids_list = [
                    {
                        'name': 'Endoso ' + invoice.partner_id.name,
                        'move_id': endoso.id,
                        'partner_id': invoice.partner_id.id,
                        'account_id': invoice.partner_id.property_account_receivable_id.id,
                        'credit': total_porcentaje,
                    },
                    {
                        'name': 'Endoso ' + cliente.name,
                        'move_id': endoso.id,
                        'partner_id': cliente.id,
                        'account_id': cliente.property_account_receivable_id.id,
                        'debit': total_porcentaje,
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
                    'res_id': endoso.id,
                    'target': 'current',
                    'line_ids': lineas
                }
