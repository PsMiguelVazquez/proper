# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from lxml.objectify import fromstring
import base64
class UploadInvoice(models.TransientModel):
    _name = 'upload.invoice.wizard'
    _description = 'Sube una adjuntos para asignarla a ordenes de venta'
    client_id= fields.Many2one('res.partner', 'Cliente')
    provider_id= fields.Many2one('res.partner', 'Proveedor')
    sale_ids = fields.Many2many('sale.order')
    purchase_ids = fields.Many2many('purchase.order')
    order_lines = fields.Many2many('sale.order.line')
    purchase_lines = fields.Many2many('purchase.order.line')
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
    total_ordenes = fields.Float('Total', compute='_compute_total_ordenes')
    total_lineas = fields.Float('Total líneas', compute='_compute_total_lineas')
    mensaje_error = fields.Text('')
    reparar_factura = fields.Boolean('Reparar factura', default=False)
    invoice_ids = fields.Many2one('account.move')
    tipo = fields.Selection(string='Tipo', selection=[('purchase_order','Orden de compra'),('sale_order','Orden de venta')])
    margen = fields.Float('Margen de redondeo')

    @api.depends('order_lines', 'purchase_lines')
    def _compute_total_lineas(self):
        for record in self:
            if record.order_lines:
                self.total_lineas = sum(self.order_lines.mapped('price_total'))
            elif record.purchase_lines:
                self.total_lineas = sum(self.purchase_lines.mapped('price_total'))
            else:
                self.total_lineas = 0

    @api.depends('sale_ids')
    def _compute_total_ordenes(self):
        for record in self:
            if record.sale_ids:
                self.total_ordenes = sum(self.sale_ids.mapped('amount_total'))
            else:
                self.total_ordenes = sum(self.purchase_ids.mapped('amount_total'))


    def get_node(self,cfdi_node, attribute, namespaces):
        if hasattr(cfdi_node, 'Complemento'):
            node = cfdi_node.Complemento.xpath(attribute, namespaces=namespaces)
            return node[0] if node else None
        else:
            return None

    @api.constrains('adjuntos')
    def _check_adjuntos(self,):
        for record in self:
            total_xmls = len(record.adjuntos.filtered(lambda x: x.mimetype == 'application/xml'))
            if total_xmls > 1:
                raise ValidationError('Solo puede subir un archivo de tipo XML')
            if total_xmls == 0:
                raise ValidationError('Debe subir un archivo de tipo XML')


    def validate(self):
        valid = True
        message = ''
        if self.sale_ids:
            total_validar = sum(self.sale_ids.mapped('amount_total'))
        else:
            total_validar = sum(self.purchase_ids.mapped('amount_total'))
        if not (round(total_validar, 2) >= self.monto- self.margen and round(total_validar, 2) <=  self.monto + self.margen):
        # if not (round(total_validar,2) - self.monto >= -self.margen and  round(total_validar,2) - self.monto <= self.margen):
            valid =  False
            message += '\nNo coinciden los montos. Monto total de las facturas seleccionadas: ' + str(total_validar) + ' Monto en el archívo XML: ' + str(self.monto)
        return valid, message

    def upload_invoice_and_assign(self):
        invoice_id = self.env['account.move'].search([('ref', '=', self.ref)])
        if self.reparar_factura:
            invoice_id = self.invoice_ids
            if invoice_id and self.client_id:
                invoice_id.write({'edi_error_message': None,
                                  'edi_blocking_level': None,
                                  'edi_error_message': None,
                                  'edi_error_message': None
                                  })
                invoice_id.edi_document_ids.filtered(lambda d: d.error).write({'error': None})
                acc_edi_doc_id = self.env['account.edi.document'].search(
                    [('move_id', '=', invoice_id.id), ('edi_format_id', '=', 2)])
                for adjunto in self.adjuntos:
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
        else:
            valid, message = self.validate()
            if valid:
                if self.tipo == 'purchase_order':
                    journal_id = 2
                    tipo_movimiento = 'in_invoice'
                    self.tipo_movimiento = tipo_movimiento
                    invoice_origin = ', '.join(self.purchase_ids.mapped('name'))
                else:
                    partners_id = self.sale_ids.mapped('partner_id.id')
                    if len(partners_id) == 0:
                        raise UserError('No existe el cliente')
                    if len(partners_id) > 1:
                        raise UserError('No se puede subir una factura si los clientes no son los mismos')
                    #Se obtienen los archivos xml para facturas mexicanas emitidas
                    attachments = self.env['ir.attachment'].search([
                        ('res_model', '=', 'account.move'),
                        ('mimetype', '=', 'application/xml'),
                        ('description', 'ilike', 'factura mexicana')
                    ])
                    '''
                        Como el valor del UUID no es un dato almaceado se tiene que extraer de los archivos
                        Se crea una tupla (UUID,ID DE FACTURA) para poder buscar si ya está registrado un UUID
                        #######################
                        ######## TO DO ########
                        - Optimizar este proceso
                        - Idea: Puede ser con el checksum del adjunto pero no garantiza que no se suban UUID repetidos
                        ######################
                        #######################
                    '''
                    tupla_uuids_facturas = [
                        (self.get_node(
                            fromstring(base64.decodebytes(attachment.with_context(bin_size=False).datas)),
                            'tfd:TimbreFiscalDigital[1]',
                            {'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'},
                        ).get('UUID'), attachment.res_id)
                        for attachment in attachments
                    ]
                    uuids = [uuids_fact[0] for uuids_fact in tupla_uuids_facturas]
                    #Si ya existe el folio fiscal muestra un mensaje e indica en cuál factura
                    if self.folio_fiscal in uuids:
                        index = uuids.index(self.folio_fiscal)
                        id_am = tupla_uuids_facturas[index][1]
                        am = self.env['account.move'].browse(id_am)
                        raise UserError(f'Ya existe una factura {am.name} con ese folio fiscal.')

                    journal_id = 1
                    invoice_origin = ', '.join(self.sale_ids.mapped('name'))
                if self.client_id:                    
                    self.sale_ids.partner_id = self.client_id
                    self.sale_ids.partner_invoice_id = self.client_id
                    invoice_id = self.sale_ids._create_invoices()
                    invoice_id.ref = self.ref
                    invoice_id.x_referencia = self.ref
                    invoice_id.invoice_date = self.fecha_factura
                    invoice_id.partner_id = self.client_id
                    if invoice_id:
                        invoice_id.action_post()
                        acc_edi_doc_id = self.env['account.edi.document'].search([('move_id', '=', invoice_id.id), ('edi_format_id', '=', 2)])
                        for adjunto in self.adjuntos:
                            attachment = self.env['ir.attachment'].create({
                                'name': adjunto.name,
                                'type': 'binary',
                                'datas': adjunto.datas,
                                'res_model': 'account.move',
                                'res_id': invoice_id.id,
                                'mimetype': adjunto.mimetype,
                                'description': f'CFDI de factura mexicana generado para el documento {invoice_id.name}'
                            })
                            if adjunto.mimetype == 'application/xml':
                                ### Account
                                acc_edi_doc_dict = {
                                    'state': 'sent',
                                    'attachment_id': attachment.id,
                                }
                                acc_edi_doc_id.write(acc_edi_doc_dict)
                    return {
                        'name': _('Factura'),
                        'view_mode': 'form',
                        'view_id': self.env.ref('account.view_move_form').id,
                        'res_model': 'account.move',
                        'type': 'ir.actions.act_window',
                        'nodestroy': True,
                        'res_id': invoice_id.id,
                        'target': 'current',
                    }
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
                if xmls and xmls[0]:
                    try:
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

                        cfdi_ref = (serie if serie else '') + (folio if folio else '')

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

                        partner_id = self.env['res.partner']
                        provider_id = self.env['res.partner']
                        if self.tipo == 'purchase_order':
                            provider_id = self.env['res.partner'].search([('vat', '=', emisor_vat)]).filtered(
                                lambda x: x.company_type == 'company')
                            self.purchase_ids = self.env['purchase.order'].search(
                                [('id', 'in', self.env.context.get('active_ids'))])
                            self.purchase_lines = self.purchase_ids.mapped('order_line')
                            self.provider_id = provider_id
                        else:
                            partner_id = self.env['res.partner'].search([('vat', '=', receptor_vat)]).filtered(lambda x: x.company_type == 'company')
                        if partner_id:
                            self.client_id = partner_id[0]
                        elif provider_id:
                            self.client_id = provider_id[0]
                        else:
                            self.mensaje_error = 'No existe en el sistema el cliente con RFC ' + receptor_vat + ' en el XML. Tiene que darlo de alta como CLIENTE antes de subir esta factura'

                        l10n_mx_edi_payment_method_id = self.env['l10n_mx_edi.payment.method'].search([('code', '=', FormaPago)])
                        partner_data = self.env['res.partner'].search([('id', '=', self.client_id.id)])
                        property_payment_term_id = partner_data['property_payment_term_id']
                        # if property_payment_term_id:
                        #     property_payment_term_id = property_payment_term_id[0]
                        # else:
                        #     property_payment_term_id = 1

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
                        self.terminos_pago = property_payment_term_id.id if property_payment_term_id else 1
                        self.terminos_pago_id = property_payment_term_id.id
                        self.sale_ids = self.env['sale.order'].search([('id', 'in', self.env.context.get('active_ids'))])
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
                        w.sale_ids = self.sale_ids
                        w.order_lines = self.order_lines
                        w.purchase_ids = self.purchase_ids
                    except:
                        self.mensaje_error ='Error al obtener los datos del documento XML. Compruebe la estructura del archivo'
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
                self.mensaje_error= None
