# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

# MIGRACIÓN V19: los campos `x_referencia`, `x_comentarios`, `x_atencion`,
# `x_observaciones`, `x_studio_sociedad`, `x_studio_numero_proveedor`,
# `x_studio_numero_pedido`, `x_studio_numero_entrada_sap`,
# `x_studio_numero_remision_1`, `x_studio_orden_de_compra`,
# `x_studio_almacn`, `x_fecha_pago_pro`, `x_tipo_de_relacion` y
# `x_estado_actuali_cli` eran personalizaciones de Odoo Studio (sin código de
# módulo en v15). A partir de esta migración se formalizan aquí como campos
# reales -mismo nombre técnico y tipo exactos que en el export de Studio-,
# de modo que al actualizar la base de datos de producción real Odoo tome
# las columnas ya existentes sin perder datos. `x_studio_n_orden_de_compra`
# vive en `sale.order` (formalizado en `sale_purchase_confirm`, Lote 3);
# por eso este módulo declara esa dependencia explícita y su
# instalación/pruebas quedan diferidas hasta que esté migrado.


class AccountMove(models.Model):
    _inherit = 'account.move'
    remision_name = fields.Char(string='Número de remisión', compute='_compute_remision_name', store=True)

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
    duplicated_from = fields.Many2one('account.move')
    es_anticipo = fields.Boolean(string='¿Es anticipo?', default=False)
    x_studio_n_orden_de_compra = fields.Char(string="Orden de compra", compute="compute_orden_compra")

    x_referencia = fields.Char(string='Referencia')
    x_comentarios = fields.Text(string='Comentarios')
    x_atencion = fields.Text(string='Atención')
    x_observaciones = fields.Text(string='Observaciones')
    x_studio_sociedad = fields.Char(string='Sociedad')
    x_studio_numero_proveedor = fields.Char(string='Número de proveedor')
    x_studio_numero_pedido = fields.Char(string='Número de pedido')
    x_studio_numero_entrada_sap = fields.Char(string='Número de entrada a SAP')
    x_studio_numero_remision_1 = fields.Char(string='Número de remisión (Studio)')
    x_studio_orden_de_compra = fields.Char(string='Orden de Compra')
    x_studio_almacn = fields.Char(string='Almacén', compute='_compute_x_studio_almacn', store=True)
    x_fecha_pago_pro = fields.Date(string='Fecha estimada de Pago')
    x_tipo_de_relacion = fields.Char(string='Tipo de relación')
    # MIGRACIÓN V19: `x_estado_actuali_cli` se quita de aquí por duplicado:
    # ya se declara en `sale_purchase_confirm/models/account_move.py`
    # (dependencia de este módulo), tener el mismo campo `related=` en dos
    # módulos sin relación de dependencia entre sí hacía que el orden de
    # carga decidiera cuál definición "ganaba", generando el warning
    # "selection attribute will be ignored as the field is related" por
    # duplicado (una vez por cada declaración).
    # MIGRACIÓN V19: `x_plazo_pago` (related a
    # `invoice_payment_term_id.x_nombre_corto` según el export de Studio) se
    # había omitido en la formalización inicial; se agrega aquí. Se declara
    # sin `related=` porque `on_change_l10n_mx_edi_payment_method_id` le
    # asigna un valor propio (`'PUE'`) en un caso, distinto del related puro.
    x_plazo_pago = fields.Char(string='Política de pago')

    @api.depends('sale_id.warehouse_id.code')
    def _compute_x_studio_almacn(self):
        for record in self:
            record.x_studio_almacn = record.sale_id.warehouse_id.code if record.sale_id else False

    def compute_orden_compra(self):
        for record in self:
            if record.sale_id:
                record.x_studio_n_orden_de_compra = record.sale_id.x_studio_n_orden_de_compra
            else:
                record.x_studio_n_orden_de_compra = ''

    @api.onchange('l10n_mx_edi_payment_method_id')
    def on_change_l10n_mx_edi_payment_method_id(self):
        # MIGRACIÓN V19: el id crudo 20 dependía del orden de carga de
        # `l10n_mx_edi_payment_method_data.xml`; se resuelve por xmlid
        # (`payment_method_anticipos`, código SAT 30 - "Aplicación de
        # anticipos") para no depender de IDs autonuméricos.
        anticipos_method = self.env.ref(
            "l10n_mx_edi.payment_method_anticipos", raise_if_not_found=False
        )
        for record in self:
            partner = record.partner_id
            if anticipos_method and record.l10n_mx_edi_payment_method_id.id == anticipos_method.id:
                record.invoice_payment_term_id = 1
                record.x_plazo_pago = 'PUE'
            else:
                record.invoice_payment_term_id = partner.property_payment_term_id
                record.x_plazo_pago = partner.x_nombre_corto_tpago

    @api.depends('write_date')
    def _compute_remision_name(self):
        for record in self:
            if record.move_type == 'out_invoice':
                record['remision_name'] = str(record.id)
            else:
                record['remision_name'] = ''

    def _compute_cantidad_facturada_total(self):
        for record in self:
            if record.invoice_line_ids:
                record.cantidad_facturada_total = sum(record.invoice_line_ids.mapped('quantity'))
            else:
                record.cantidad_facturada_total = 0

    def _compute_movimientos_almacen(self):
        for record in self:
            if record.sale_id:
                salename = record.sale_id.name
            else:
                salename = ''
            domain = [
                '|', ('x_studio_facturas', '=', record.id),
                '|', ('origin', '=', record.name), ('origin', '=', salename),
                ('picking_type_code', 'in', ['outgoing', 'incoming']),
            ]
            record.movimientos_almacen = self.env['stock.picking'].search(domain)

    def _compute_fecha_entrega_mercancia(self):
        for record in self:
            fecha_entrega_mercancia_html = ''
            mov_out = self.env['stock.picking'].search([
                ('x_studio_facturas', '=', record.id),
                ('state', '=', 'done'),
                ('picking_type_code', '=', 'outgoing'),
            ])
            if mov_out and mov_out[0].date_done:
                record.fecha_entrega_mercancia = mov_out[0].date_done
                record.fecha_recepcion_cliente = mov_out[0].fecha_recepcion_cliente
            else:
                record.fecha_entrega_mercancia = None
                record.fecha_recepcion_cliente = None
            fecha_entrega_mercancia_html = "<table class='table' style='width: 100%'><thead><tr><th>OUT</th><th>Fecha OUT</th><th>Fecha recepción del cliente</th><tr></thead><tbody>"
            for mov in mov_out:
                fecha_entrega_mercancia_html += "<tr><td>" + mov.name +"</td><td>" + (mov.date_done.strftime("%d/%m/%Y") if mov.date_done else '')+"</td><td>" + (mov.fecha_recepcion_cliente.strftime("%d/%m/%Y") if mov.fecha_recepcion_cliente else '') + "</td></tr>"
            fecha_entrega_mercancia_html += "</tbody></table>"
            self.fecha_entrega_mercancia_html = fecha_entrega_mercancia_html

    def repair_invoice(self):
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
        # MIGRACIÓN V19: el flujo de cancelación de CFDI de `l10n_mx_edi` fue
        # completamente reescrito. En 15.0, las cancelaciones con motivo 03/04
        # no se podían enviar al SAT vía API, por lo que este módulo forzaba
        # manualmente los campos de estado (`l10n_mx_edi_sat_status`,
        # `edi_state`, `edi_web_services_to_process`, `account.edi.document`)
        # después de que el contador cancelaba el CFDI directamente en el
        # portal del SAT. En 19.0:
        #   - `l10n_mx_edi` ya NO usa el framework genérico `account_edi`
        #     (no depende de él, ver su `__manifest__.py`); los campos
        #     `edi_state`/`edi_document_ids`/`l10n_mx_edi_sat_status` nunca
        #     se pueblan para facturas MX, así que escribirlos manualmente
        #     ya no tiene ningún efecto real sobre el estado del CFDI.
        #   - `l10n_mx_edi_cfdi_state` y `l10n_mx_edi_invoice_cancellation_reason`
        #     ahora son campos calculados (`compute`) derivados del propio
        #     documento de cancelación (`l10n_mx_edi.document`), no se pueden
        #     "forzar" con `write()`.
        #   - El propio núcleo ahora sí admite solicitar la cancelación con
        #     los 4 motivos (01-04) vía API a través del wizard nativo
        #     `l10n_mx_edi.invoice.cancel` (ver
        #     `enterprise/l10n_mx_edi/wizard/l10n_mx_edi_invoice_cancel.py`),
        #     disparado por el botón/método estándar `button_request_cancel()`.
        # Se conserva la validación de negocio original (no cancelar si no se
        # ha regresado toda la mercancía al almacén) y se delega la
        # cancelación real al mecanismo nativo en lugar de forzar campos.
        account_move = self.env['account.move'].browse(self.env.context.get('active_ids'))
        if not account_move.motivo_cancelacion or account_move.motivo_cancelacion not in ('03','04'):
            raise UserError('Para marcar esta factura como cancelada debe tener el motivo de cancelación 03 o 04')
        if account_move.motivo_cancelacion == '03':
            movs_out = self.env['stock.picking'].search([('origin', '=', account_move.sale_id.name)]).filtered(
                                    lambda x: x.picking_type_code == 'outgoing' and x.state == 'done')
            if movs_out:
                suma_productos_entregados = 0
                suma_productos_retornados = 0
                for move_out in movs_out:
                    # MIGRACIÓN V19: `move_line_ids_without_package` fue
                    # eliminado; `qty_done` -> `quantity` + `picked`.
                    suma_productos_entregados += sum(
                        move_out.move_line_ids.filtered("picked").mapped("quantity")
                    )

                movs_in = self.env['stock.picking'].search([('sale_id', '=', account_move.sale_id.id)]).filtered(
                                    lambda x: x.picking_type_code == 'incoming' and x.state == 'done')
                if movs_in:
                    for mov_in in movs_in:
                        suma_productos_retornados += sum(
                            mov_in.move_line_ids.filtered("picked").mapped("quantity")
                        )

                if suma_productos_retornados <  suma_productos_entregados:
                    raise UserError('No se puede marcar como cancelada esta factura si no se ha regresado toda la mercancia al almacén')

        # `button_request_cancel()` dispara el flujo nativo de solicitud de
        # cancelación (wizard `l10n_mx_edi.invoice.cancel`), que gestiona la
        # transición de estado real (incluyendo `state='cancel'`) una vez
        # confirmada; forzar `state` aquí de antemano ya no aplica.
        return account_move.button_request_cancel()

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
        for line in invoice.invoice_line_ids:
            product_dict = {
                'sequence': 10,
                'name': line.name,
                'quantity': line.quantity,
                'product_id': line.product_id.id,
                'price_unit': line.price_unit,
                'tax_ids': [(6, 0, line.tax_ids.ids)],
                'product_uom_id': line.product_uom_id.id
            }
            product_list.append((0, 0, product_dict))
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
            'x_observaciones': invoice.x_observaciones,
            'duplicated_from': invoice.id,
            'partner_bank_id': invoice.partner_bank_id.id if invoice.partner_bank_id else None,
            'invoice_origin': invoice.invoice_origin
        }
        invoice_id = self.env['account.move'].create(invoice_dict)
        invoice.sale_id.order_line.invoice_lines |= invoice_id.invoice_line_ids
        new_invoice_msg = (
                              "This invoice has been created from: <a href=# data-oe-model=sale.order data-oe-id=%d>%s</a>") % (
                              invoice.sale_id.id, invoice.sale_id.name)
        invoice_id.message_post(body=new_invoice_msg, message_type="notification")
        invoice_msg = (
                          "This invoice has been duplicated from: <a href=# data-oe-model=account.move data-oe-id=%d>%s</a>") % (
                          invoice.id, invoice.name)
        invoice_id.message_post(body=invoice_msg, message_type="notification")

        if invoice_id:
            if not self.env['stock.picking'].search([('origin', '=', invoice.name)
                                                        , ('picking_type_code', '=', 'incoming')
                                                        , ('location_dest_id.id', '=', 69)
                                                     ]):
                # MIGRACIÓN V19: `immediate_transfer` y el wizard
                # `stock.immediate.transfer` fueron eliminados; `move_lines`
                # -> `move_ids`; `quantity_done` -> `quantity` + `picked`.
                move_lines_d = []
                for line in invoice_id.invoice_line_ids:
                    move_line_vals = {
                        'name': line.product_id.name,
                        "product_id": line.product_id.id,
                        "product_uom_qty": line.quantity,
                        "quantity": line.quantity,
                        "picked": True,
                        "product_uom": line.product_id.uom_id.id,
                        'location_id': 4,
                        'location_dest_id': 69

                    }
                    move_lines_d.append((0, 0, move_line_vals))
                picking = self.env['stock.picking'].create({
                    'location_id': 4,
                    'origin': invoice.name,
                    'location_dest_id': 69,
                    'picking_type_id': 11,
                    'move_type': 'direct',
                    'move_ids': move_lines_d,
                })
                picking.button_validate()
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
        # MIGRACIÓN V19: `res.partner.l10n_mx_edi_addenda` (Many2one) ->
        # `l10n_mx_edi_addenda_ids` (Many2many): un partner puede tener
        # varias addendas configuradas.
        if self.partner_id.l10n_mx_edi_addenda_ids:
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

    def _l10n_mx_edi_cfdi_invoice_try_send(self):
        # MIGRACIÓN V19: en 15.0 esta validación vivía en un override de
        # `button_process_edi_web_services()`, el punto de entrada genérico
        # que usaba el `account_edi` de esa época para timbrar. En 19.0
        # `l10n_mx_edi` ya no pasa por ese framework genérico (no depende de
        # `account_edi`); el timbrado real ocurre en este método. Se traslada
        # aquí la misma validación para conservar el comportamiento.
        if self.move_type == 'out_invoice' and not self.es_anticipo:
            self.valida_addenda()
        return super()._l10n_mx_edi_cfdi_invoice_try_send()

    @api.depends('remision_name', 'state', 'move_type')
    def _compute_display_name(self):
        # MIGRACIÓN V19: `name_get()` fue removido del core; el equivalente
        # es sobreescribir `_compute_display_name`, llamando a `super()`
        # primero para no perder el formato estándar del resto de casos.
        super()._compute_display_name()
        for record in self:
            if record.state == 'draft' and record.move_type == 'out_invoice':
                record.display_name = record.remision_name
