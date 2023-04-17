# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from lxml.objectify import fromstring
class UploadInvoice(models.TransientModel):
    _name = 'upload.invoice.wizard'
    _description = 'Sube una adjuntos para asignarla a ordenes de venta'
    client_id= fields.Many2one('res.partner', 'Cliente')
    sale_ids = fields.Many2many('sale.order')
    order_lines = fields.Many2many('sale.order.line')
    adjuntos = fields.Many2many('ir.attachment')
    monto = fields.Float('Monto Total')
    subtotal = fields.Float('Subtotal')
    folio_fiscal = fields.Char('Folio fiscal')
    rfc_emisor = fields.Char('RFC Emisor')
    rfc_receptor = fields.Char('RFC Receptor')
    uso_cfdi = fields.Char('Uso de CFDI')
    metodo_pago = fields.Char('Método de pago')
    forma_pago = fields.Char('Forma de pago')
    version_cfdi = fields.Char('Versión de CFDI')
    fecha_factura = fields.Date('Fecha de adjuntos')
    ref = fields.Char('Referencia')
    terminos_pago = fields.Char('Términos de pago')
    terminos_pago_id = fields.Many2one('Id Términos de pago')
    tipo_movimiento = fields.Char('Tipo de movimiento')
    id_metodo_pago = fields.Integer('Id Método de pago')
    codigos_producto = fields.Char('Códigos de producto')


    def get_node(self,cfdi_node, attribute, namespaces):
        if hasattr(cfdi_node, 'Complemento'):
            node = cfdi_node.Complemento.xpath(attribute, namespaces=namespaces)
            return node[0] if node else None
        else:
            return None

    @api.constrains('adjuntos')
    def _check_adjuntos(self,):
        for record in self:
            if len(record.adjuntos.filtered(lambda x: x.mimetype == 'application/xml')) > 1:
                raise ValidationError('Solo puede subir un archivo de tipo XML')


    def validate(self):
        valid = True
        message = ''
        sale_orders_total = sum(self.sale_ids.mapped('amount_total'))
        if round(sale_orders_total,2) != self.monto:
            valid =  False
            message += '\nNo coinciden los montos. Monto total de las facturas seleccionadas: ' + str(sale_orders_total) + ' Monto en el archívo XML: ' + str(self.monto)
        return valid, message

    def upload_invoice_and_assign(self):
        invoice_id = self.env['account.move'].search([('ref', '=', self.ref)])
        valid, message = self.validate()
        if valid:
            if not invoice_id and self.client_id:
                product_list =[]
                for line in self.order_lines:
                    product_dict = {
                        'sequence': 10,
                        'name': line.product_id.name,
                        'quantity': 1.0,
                        'product_id': line.product_id,
                        'price_unit': line.price_unit,
                        'tax_ids': line.tax_id,
                    }
                    product_list.append(product_dict)
                invoice_dict = {
                    'invoice_date': self.fecha_factura,
                    'ref': self.ref,
                    'x_referencia': self.ref,
                    'journal_id': 1,
                    'posted_before': False,
                    'invoice_payment_term_id': self.terminos_pago_id,
                    'partner_id': self.client_id,
                    'move_type': self.tipo_movimiento,
                    'l10n_mx_edi_payment_method_id': self.id_metodo_pago,
                    'l10n_mx_edi_payment_policy': self.metodo_pago,
                    'l10n_mx_edi_usage': self.uso_cfdi,
                    'version_cfdi': self.version_cfdi,
                    'invoice_line_ids': product_list,
                    'l10n_mx_edi_cfdi_uuid': self.folio_fiscal
                }
                invoice_id = self.env['account.move'].create(invoice_dict)
                if invoice_id:
                    ap = invoice_id.action_post()
                    print(ap)
                acc_edi_doc_id = self.env['account.edi.document'].search([('move_id', '=', invoice_id.id), ('edi_format_id', '=', 2)])
                for adjunto in self.adjuntos:
                    # adjunto.update({'res_model': 'account.move', 'res_id' : invoice_id, 'description': ('Mexican invoice CFDI generated for the %s document.') % self.ref})
                    attachment = self.env['ir.attachment'].create({
                        'name': adjunto.name,
                        'type': 'binary',
                        'datas': adjunto.datas,
                        'res_model': 'account.move',
                        'res_id': invoice_id.id,
                        'mimetype': adjunto.mimetype,
                    })
                    if adjunto.mimetype == 'application/xml':
                        ### Account
                        acc_edi_doc_dict = {
                            'state': 'sent',
                            'attachment_id': attachment.id,
                        }
                        acc_edi_doc_id.write(acc_edi_doc_dict)
            if invoice_id and self.client_id:
                invoice_dict = {
                    'invoice_date': self.fecha_factura,
                    'ref': self.ref,
                    'x_referencia': self.ref,
                    'journal_id': 1,
                    'posted_before': False,
                    'invoice_payment_term_id': self.terminos_pago_id,
                    'partner_id': self.client_id,
                    'move_type': self.tipo_movimiento,
                    'l10n_mx_edi_payment_method_id': self.id_metodo_pago,
                    'l10n_mx_edi_payment_policy': self.metodo_pago,
                    'l10n_mx_edi_usage': self.uso_cfdi,
                    'version_cfdi': self.version_cfdi,
                }
                self.env['account.move'].write(invoice_dict)

                for sale_order_id in self.sale_ids:
                    sale_order_dict = {
                        'invoice_ids': invoice_id,
                        'invoice_status': 'invoiced',
                        'x_estado_surtido': 'surtir',
                    }
                    for sale_order_line_id in sale_order_id.order_line:
                        sale_order_line_id.write({'invoice_lines': invoice_id.line_ids})
                    sale_order_id.write(sale_order_dict)
                    invoice_msg = (
                                          "This invoice has been created from: <a href=# data-oe-model=sale.order data-oe-id=%d>%s</a>") % (
                                      sale_order_id.id, sale_order_id.name)
                    invoice_id.message_post(body=invoice_msg ,type="notification")
        else:
            raise UserError(message)

    @api.onchange('sale_ids')
    def on_change_sale_ids(self):
        for record in self:
            self.order_lines = self.order_lines = self.sale_ids.mapped('order_line')

    @api.onchange('adjuntos')
    def on_change_factura(self):
        for record in self:
            if record.adjuntos:
                xmls = record.adjuntos.filtered(lambda x: x.mimetype == 'application/xml')
                pdfs = record.adjuntos.filtered(lambda x: x.mimetype == 'application/pdf')
                if xmls[0]:
                    cfdi_node = fromstring(xmls[0].raw)
                    emisor_node = cfdi_node.Emisor
                    ######### Lista de productos en el XML ########
                    self.codigos_producto = cfdi_node['Conceptos']['Concepto']

                    receptor_node = cfdi_node.Receptor
                    tfd_node = self.get_node(
                        cfdi_node,
                        'tfd:TimbreFiscalDigital[1]',
                        {'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'},
                    )

                    ####  Folio y serie
                    serie = cfdi_node.get('Serie')
                    folio = cfdi_node.get('Folio')
                    cfdi_ref = serie + folio

                    ####  MetodoPago
                    MetodoPago = cfdi_node.get('MetodoPago')

                    ####  FormaPago
                    FormaPago = cfdi_node.get('FormaPago')

                    ####  Version
                    cfdi_version = 'CFDI (' + cfdi_node.get('Version') + ')'

                    ##### Document type
                    cfdi_type = cfdi_node.get('TipoDeComprobante')
                    if cfdi_type == 'I':
                        move_type = 'out_invoice'
                    if cfdi_type == 'E':
                        move_type = 'out_refund'

                    SubTotal = cfdi_node.get('SubTotal')
                    total = cfdi_node.get('Total')

                    cfdi_date = cfdi_node.get('Fecha')

                    ####  Comprobante info

                    # Emisor
                    emisor_name = emisor_node.get('Nombre', emisor_node.get('Nombre'))
                    emisor_vat = emisor_node.get('Rfc', emisor_node.get('rfc'))

                    # Receptor
                    receptor_name = receptor_node.get('Nombre', receptor_node.get('Nombre'))
                    receptor_vat = receptor_node.get('Rfc', emisor_node.get('rfc'))
                    receptor_usocfdi = receptor_node.get('UsoCFDI', emisor_node.get('UsoCFDI'))

                    cfdi_uuid = tfd_node.get('UUID')

                    partner_id = self.env['res.partner'].search([('vat','=',receptor_vat)])
                    if partner_id:
                        self.client_id = partner_id[0]

                    l10n_mx_edi_payment_method_id = self.env['l10n_mx_edi.payment.method'].search([('code', '=', FormaPago)])
                    partner_data = self.env['res.partner'].search([('id', '=', self.client_id.id)])
                    property_payment_term_id = partner_data['property_payment_term_id']
                    if property_payment_term_id:
                        property_payment_term_id = property_payment_term_id[0]
                    else:
                        property_payment_term_id = 1

                    self.folio_fiscal = cfdi_uuid
                    self.monto = total
                    self.fecha_factura = cfdi_date
                    self.rfc_emisor = emisor_vat
                    self.rfc_receptor = receptor_vat
                    self.uso_cfdi = receptor_usocfdi
                    self.metodo_pago = MetodoPago
                    self.forma_pago = FormaPago
                    self.version_cfdi = cfdi_version
                    self.ref = cfdi_ref
                    self.tipo_movimiento = move_type
                    self.subtotal = SubTotal
                    self.id_metodo_pago = l10n_mx_edi_payment_method_id.id
                    self.terminos_pago = property_payment_term_id.id
                    self.terminos_pago_id = property_payment_term_id.id
                    self.sale_ids = self.env['sale.order'].search([('id','in',self.env.context.get('active_ids'))])
                    self.order_lines = self.sale_ids.mapped('order_line')

                    w = self.env['upload.invoice.wizard'].search([('id', '=', self.id.origin)])
                    w.folio_fiscal = cfdi_uuid
                    w.monto = total
                    w.fecha_factura = cfdi_date
                    w.rfc_emisor = emisor_vat
                    w.rfc_receptor = receptor_vat
                    w.uso_cfdi = receptor_usocfdi
                    w.metodo_pago = MetodoPago
                    w.forma_pago = FormaPago
                    w.version_cfdi = cfdi_version
                    w.ref = cfdi_ref
                    w.tipo_movimiento = move_type
                    w.subtotal = SubTotal
                    w.client_id = self.client_id
                    w.id_metodo_pago = self.id_metodo_pago
                    w.terminos_pago = self.terminos_pago
                    w.terminos_pago_id = property_payment_term_id.id
                    w.codigos_producto = self.codigos_producto
                    w.sale_ids =self.sale_ids
                    w.order_lines = self.order_lines
            else:
                self.folio_fiscal = ''
                self.monto = 0.0
                self.fecha_factura = None
                self.rfc_emisor = ''
                self.rfc_receptor = ''
                self.uso_cfdi = ''
                self.metodo_pago = ''
                self.forma_pago = ''
                self.version_cfdi = ''
                self.client_id = None
                self.ref = ''
                self.tipo_movimiento = ''
                self.subtotal = 0.0
                self.client_id = None
                self.id_metodo_pago = None
                self.terminos_pago = ''
                self.order_lines = None
                self.sale_ids = None
