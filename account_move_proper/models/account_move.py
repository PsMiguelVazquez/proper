# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class AccountMove(models.Model):
    _inherit = 'account.move'
    remision_name = fields.Char(string='Número de remisión', compute='_compute_remision_name', store=True)
    @api.depends('state')
    def _compute_remision_name(self):
        for record in self:
            record['remision_name'] = 'Remisión - ' + str(record.id)

    motivo_cancelacion = fields.Selection(string='Motivo de cancelación', selection=[('01','01 - Comprobante emitido con errores con relación'),
                                                                                      ('02','02 - Comprobante emitido con errores sin relación'),
                                                                                      ('03','03 - No se llevó a cabo la operación'),
                                                                                      ('04','04 - Operación nominativa relacionada en la factura global')])
    fecha_entrega_mercancia = fields.Date(string='Fecha de entrega de la mercancía', compute='_compute_fecha_entrega_mercancia')
    fecha_recepcion_credito = fields.Date(string='Fecha de recepción de evidencias')
    fecha_recepcion_cliente = fields.Date(string='Fecha de recepción del cliente', compute='_compute_fecha_entrega_mercancia')
    fecha_confirmacion_cancelacion = fields.Date(string='Fecha de confirmación de cancelación ante el SAT')
    ejecutivo_cuenta = fields.Char(string='Ejecutivo de cuenta', related='partner_id.x_nom_corto_agente_venta')
    fecha_entrega_mercancia_html = fields.Html(string='Fechas de entrega', compute='_compute_fecha_entrega_mercancia')
    movimientos_almacen = fields.Many2many(comodel_name='stock.picking', compute='_compute_movimientos_almacen')
    cantidad_facturada_total = fields.Integer(string='Cantidad facturada total',compute='_compute_cantidad_facturada_total')

    def _compute_cantidad_facturada_total(self):
        for record in self:
            if record.invoice_line_ids:
                record.cantidad_facturada_total = sum(record.invoice_line_ids.mapped('quantity'))
            else:
                record.cantidad_facturada_total = 0

    def _compute_movimientos_almacen(self):
        for record in self:
            record.movimientos_almacen = self.env['stock.picking'].search([('x_studio_facturas','=',record.id),('picking_type_code','in',['outgoing', 'incoming'])])
    def _compute_fecha_entrega_mercancia(self):
        for record in self:
            fecha_entrega_mercancia_html = ''
            mov_out = self.env['stock.picking'].search([('x_studio_facturas','=',record.id),('state','=','done'),('picking_type_code','=','outgoing')])
            if mov_out and mov_out[0].date_done:
                record.fecha_entrega_mercancia = mov_out[0].date_done
                record.fecha_recepcion_cliente = mov_out[0].fecha_recepcion_cliente
            else:
                record.fecha_entrega_mercancia = None
                record.fecha_recepcion_cliente = None
            fecha_entrega_mercancia_html = "<table class='table' style='width: 100%'><thead><tr><th>OUT</th><th>Fecha OUT</th><th>Fecha recepción del cliente</th><tr></thead><tbody>"
            for mov in mov_out:
                # link = ("dd<a href=# data-oe-model=stock.picking data-oe-id=%d>%s</a>") % (mov.id, mov.name)
                fecha_entrega_mercancia_html += "<tr><td>" + mov.name +"</td><td>" + (mov.date_done.strftime("%d/%m/%Y") if mov.date_done else '')+"</td><td>" + (mov.fecha_recepcion_cliente.strftime("%d/%m/%Y") if mov.fecha_recepcion_cliente else '') + "</td></tr>"
            fecha_entrega_mercancia_html += "</tbody></table>"
            self.fecha_entrega_mercancia_html = fecha_entrega_mercancia_html



    # def action_post(self):
    #     super(AccountMove, self).action_post()

    def repair_invoice(self):
        # if self.env['account.move'].search([('sale_id','in',self.ids)]).filtered(lambda x: x.state == 'posted'):
        #     raise UserError(_('No se puede subir una factura externa si la orden ya tiene una factura publicada'))
        self.env['account.move'].search([('id','=',self.env.context.get('active_id'))])
        w = self.env['upload.invoice.wizard'].create({'subtotal': 0.0, 'monto': 0.0,'reparar_factura':True, 'invoice_ids': self.env.context.get('active_id') })
        view = self.env.ref('upload_invoice_wizard.view_upload_invoice_sale_form')
        return {
            'name': _('Reparar Factura'),
            'type': 'ir.actions.act_window',
            'res_model': 'upload.invoice.wizard',
            'view_mode': 'form',
            'res_id': w.id,
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new'
        }


    def mark_as_cancelled(self):
        account_move = self.env['account.move'].browse(self.env.context.get('active_ids'))
        # if not account_move.:
        if not account_move.motivo_cancelacion or account_move.motivo_cancelacion not in ('03','04'):
            raise UserError('Para marcar esta factura como cancelada debe tener el motivo de cancelación 03 o 04')
        if account_move.motivo_cancelacion == '03':
            movs_out = self.env['stock.picking'].search([('origin', '=', account_move.sale_id.name)]).filtered(
                                    lambda x: x.picking_type_code == 'outgoing' and x.state == 'done')
            if movs_out:
                suma_productos_entregados = 0
                suma_productos_retornados = 0
                for move_out in movs_out:
                    suma_productos_entregados += sum(move_out.move_line_ids_without_package.mapped('qty_done'))


                movs_in = self.env['stock.picking'].search([('sale_id', '=', account_move.sale_id.id)]).filtered(
                                    lambda x: x.picking_type_code == 'incoming' and x.state == 'done')
                if movs_in:
                    for mov_in in movs_in:
                        suma_productos_retornados += sum(mov_in.move_line_ids_without_package.mapped('qty_done'))


                if suma_productos_retornados <  suma_productos_entregados:
                    raise UserError('No se puede marcar como cancelada esta factura si no se ha regresado toda la mercancia al almacén')

        account_move.write({
            'l10n_mx_edi_sat_status': 'cancelled',
            'edi_web_services_to_process': '',
            'edi_state': 'cancelled',
            'state': 'cancel',
            'motivo_cancelacion': '04',
            'show_reset_to_draft_button': True
        })
        documents = self.env['account.edi.document']
        for move in account_move:
            for doc in move.edi_document_ids:
                if doc.state == 'to_cancel' \
                        and move.is_invoice(include_receipts=True) \
                        and doc.edi_format_id._is_required_for_invoice(move):
                    documents |= doc
        documents.write({'state': 'sent'})

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
            'partner_shipping_id':  invoice.partner_shipping_id,
            'x_comentarios': invoice.x_comentarios,
            'x_atencion': invoice.x_atencion,
            'x_observaciones': invoice.x_observaciones
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

    def valida_addenda(self):
        if self.partner_id.l10n_mx_edi_addenda:
            valid = True
            message = 'Faltan los siguientes datos de addenda:\n'
            if not self.x_studio_sociedad:
                valid = False
                message += '- Sociedad.\n'
            if not self.x_studio_numero_proveedor:
                valid = False
                message += '- Número de proveedor.\n'
            if not self.x_studio_numero_pedido:
                valid = False
                message += '- Número de pedido.\n'
            if not self.x_studio_numero_entrada_sap:
                valid = False
                message += '- Número de entrada a SAP.\n'
            if not self.x_studio_numero_remision_1:
                valid = False
                message += '- Número de remisión.\n'
            if not valid:
                raise UserError(message)
    def button_process_edi_web_services(self):
        folio_fiscal_uuid = ''
        if self.edi_state == 'to_cancel':
            '''
                Motivo de cancelación 01 - Comprobante emitido con errores con relación
                Aplica cuando la factura generada contiene errores en los datos y e debe reexpedir y se sustituirá con otra factura.
                Validaciones: 
                 1 - El folio fiscal de la factura que se quiere cancelar debe estar presente en la factura que la va a sustituir (l10n_mx_edi_origin)
                 2 - El campo CFDI de origen debe comenzar por "04|"
            '''
            if self.motivo_cancelacion == '01':
                factura_sustituta = self.env['account.move']
                if self.l10n_mx_edi_origin:
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
            folio_fiscal_uuid= self.l10n_mx_edi_cfdi_uuid
        if self.move_type == 'out_invoice':
            self.valida_addenda()
        super(AccountMove, self).button_process_edi_web_services()
        if folio_fiscal_uuid != '' :
            self.l10n_mx_edi_cfdi_uuid = folio_fiscal_uuid

    def action_retry_edi_documents_error(self):
        folio_fiscal = self.l10n_mx_edi_cfdi_uuid
        r = super(AccountMove, self).action_retry_edi_documents_error()
        if folio_fiscal and folio_fiscal != '':
            self.l10n_mx_edi_cfdi_uuid = folio_fiscal
        return r


    def name_get(self):
        result = []
        for record in self:
            if record.state == 'draft':
                name = record.remision_name
            else:
                name = record.name
            result.append((record.id, name))
        return result



