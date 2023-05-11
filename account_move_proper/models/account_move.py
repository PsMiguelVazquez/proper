# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class AccountMove(models.Model):
    _inherit = 'account.move'

    motivo_cancelacion = fields.Selection(string='Motivo de cancelación', selection=[('01','01 - Comprobante emitido con errores con relación'),
                                                                                      ('02','02 - Comprobante emitido con errores sin relación'),
                                                                                      ('03','03 - No se llevó a cabo la operación'),
                                                                                      ('04','04 - Operación nominativa relacionada en la factura global')])


    # def action_post(self):
    #     super(AccountMove, self).action_post()


    def mark_as_cancelled(self):
        account_move = self.env['account.move'].browse(self.env.context.get('active_ids'))
        # if not account_move.:
        if not account_move.motivo_cancelacion or account_move.motivo_cancelacion not in ('03','04'):
            raise UserError('Para marcar esta factura como cancelada debe tener el motivo de cancelación 03 o 04')
        print(account_move)
        account_move.write({
            'l10n_mx_edi_sat_status': 'cancelled',
            'edi_state': 'cancelled',
            'state': 'cancel',
            'motivo_cancelacion': '04',
            'show_reset_to_draft_button': True
        })

    def duplicate_invoice(self):
        product_list = []
        invoice = self.env['account.move'].search([('id','=',self.env.context.get('active_id'))])
        if not invoice.state == 'posted':
            raise UserError(
                'Para duplicar esta factura de esta manera debe estar en estado Publicado y timbrada por el SAT')
        if not invoice.l10n_mx_edi_cfdi_uuid:
            raise UserError(
                'Para duplicar esta factura de esta manera debe estar timbrada')
        if len(invoice.sale_id.invoice_ids.filtered(lambda x:x.state == 'draft')) > 0:
            raise UserError('Ya existe otro borrador de factura relacionado con este movimiento. Elimínelo primero para duplicar esta factura')
        for line in invoice.sale_id.order_line:
            product_dict = {
                'sequence': 10,
                'name': line.product_id.name,
                'quantity': line.qty_invoiced,
                'product_id': line.product_id,
                'price_unit': line.price_unit,
                'tax_ids': line.tax_id,
                'product_uom_id': line.product_uom
            }
            product_list.append(product_dict)
        invoice_dict = {
            'invoice_date': datetime.today(),
            'ref': invoice.ref,
            'x_referencia': invoice.x_referencia,
            'journal_id': 1,
            'posted_before': False,
            'invoice_payment_term_id': invoice.invoice_payment_term_id,
            'partner_id': invoice.partner_id,
            'move_type': invoice.move_type,
            'l10n_mx_edi_payment_method_id': invoice.l10n_mx_edi_payment_method_id,
            'l10n_mx_edi_payment_policy': invoice.l10n_mx_edi_payment_policy,
            'l10n_mx_edi_usage': invoice.l10n_mx_edi_usage,
            'version_cfdi': invoice.version_cfdi,
            'invoice_line_ids': product_list,
            'sale_id': invoice.sale_id,
            'partner_shipping_id':  invoice.partner_shipping_id
        }
        invoice_id = self.env['account.move'].create(invoice_dict)
        invoice.sale_id.order_line.invoice_lines |= invoice_id.invoice_line_ids
        new_invoice_msg = (
                              "This invoice has been created from: <a href=# data-oe-model=sale.order data-oe-id=%d>%s</a>") % (
                              invoice.sale_id.id, invoice.sale_id.name)
        invoice_id.message_post(body=new_invoice_msg, type="notification")
        invoice_msg = (
                          "This invoice has been duplicated from: <a href=# data-oe-model=account.move data-oe-id=%d>%s</a>") % (
                          invoice.id, invoice.name)
        invoice_id.message_post(body=invoice_msg, type="notification")

        if invoice_id:
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

    def button_process_edi_web_services(self):
        if self.edi_state == 'to_cancel':
            '''
                Motivo de cancelación 01 - Comprobante emitido con errores con relación
                Aplica cuando la factura generada contiene errores en los datos y e debe reexpedir y se sustituirá con otra factura.
                Validaciones: 
                 1 - El folio fiscal de la factura que se quiere cancelar debe estar presente en la factura que la va a sustituir (l10n_mx_edi_origin)
                 2 - El campo CFDI de origen debe comenzar por "04|"
            '''
            if self.motivo_cancelacion == '01':
                factura_sustituta = self.env['account.move'].search([('l10n_mx_edi_origin','=', '04|' + self.l10n_mx_edi_origin.split('|')[1]),('l10n_mx_edi_cfdi_uuid','!=',False)])
                if not factura_sustituta:
                    raise ValidationError('Para el motivo de cancielación 01 se necesitan seguir los siguientes pasos:\n'
                                          'Paso 1: Colocar el Folio Fiscal de la Nueva Factura en el campo “CFDI Origen”, acompañado del código 04|'
                                          '\n Cuando el sistema detecte que el campo de CFDI origen está establecido, entonces automáticamente enviará que el motivo de cancelación es el 01.')
            '''
                Motivos de cancelación 03 -  No se llevó a cabo la operción
                                       04 - Operación nominativa relacionada en la factura global
                No soportadas por Odoo hasta el 27/04/2023. Se deben cancelar estas facturas en el portal SAT
                Se mostrará una advertencia con los pasos a seguir
            '''
            if self.motivo_cancelacion in ('03','04'):
                raise ValidationError('Para los motivos 03 y 04 se deben seguir los siguientes pasos:'
                                      '\n\t1. Solicitar la cancelación con el motivo correspondiente en su portal SAT.'
                                      '\n\t2. Una vez que esté seguro que se realizó la cancelación ante el SAT de click en el menú de acciones (ícono de engrane) y seleccione la opción "Marcar como cancelado".'
                                      '\n\nAl realizar estos pasos la factura quedará como cancelada tambien en Odoo.')

        super(AccountMove, self).button_process_edi_web_services()



