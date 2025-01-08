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
    amount = fields.Float(string='Total endosado',help='Monto del endoso', compute='_compute_amount')

    def _compute_amount(self):
        for record in self:
            record.amount = record.factura.amount_residual


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
            if self.env['endoso.move'].search([('origin_invoice','=',invoice.id)]).filtered(lambda x: x.state in ('posted', 'draft')):
                raise ValidationError('Esta factura ya está endosada. Cancele el endoso relacionado')
            if not invoice.l10n_mx_edi_cfdi_uuid:
                raise ValidationError('La factura debe estar timbrada para endosarse')
            total_porcentaje = round(self.porcentaje * invoice.amount_total,2)
            journal = self.env['account.journal'].search([('name','ilike','endoso')])
            if not journal:
                raise ValidationError('No hay diario para llevar a cabo la operación Endoso')
            endoso_dict = {
                'journal_id': journal.id,
                'partner_id': self.cliente.id,
                'origin_partner_id': invoice.partner_id.id,
                # 'name': self.env['ir.sequence'].next_by_code('account.move.endoso') or _('New'),
                'origin_invoice': invoice.id,
                'amount': invoice.amount_residual,
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
                        'credit': invoice.amount_residual,
                    },
                    {
                        'name': 'Endoso ' + cliente.name,
                        'move_id': endoso.move_id.id,
                        'partner_id': cliente.id,
                        'account_id': cliente.property_account_receivable_id.id,
                        'debit': invoice.amount_residual,
                    }
                ]
                lineas = self.env['account.move.line'].create(line_ids_list)
                if not lineas:
                    raise UserError('No se pudo crear el movimiento')
                endoso.action_post()
                endoso.move_id.invoice_origin = invoice.name
                invoice.js_assign_outstanding_line(lineas[0].id)
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
