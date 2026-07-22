# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, api

from .common import studio_get


class AccountMove(models.Model):
    _inherit = 'account.move'

    x_cant_prod_facturados = fields.Integer(
        string='Cant. prod. facturados', compute='_compute_x_cant_prod_facturados')
    x_costo_total = fields.Float(
        string='Costo total factura', compute='_compute_x_costo_total')
    x_fecha_factura = fields.Text(
        string='Fecha de factura', compute='_compute_x_fecha_factura', store=True)
    x_importe_pagado = fields.Float(
        string='Importe pagado', compute='_compute_x_importe_pagado')
    x_studio_auxiliar = fields.Char(
        string='Auxiliar', compute='_compute_x_studio_auxiliar')
    x_tipo_de_comprobante = fields.Char(
        string='Tipo de comprobante', compute='_compute_x_tipo_de_comprobante', store=True)
    x_utilidad_total = fields.Float(
        string='Utilidad %', compute='_compute_x_utilidad_total', store=True)
    # MIGRACIÓN V19: etiqueta de Studio "New Entero"; el cálculo original
    # tenía la lógica real comentada y sólo dejaba el valor fijo en 1. Se
    # preserva tal cual para no perder los datos ya guardados. Sin `store`
    # a propósito (ver `common.py`): un compute sin `@api.depends` y
    # `store=True` sólo se calcula una vez, al crear el registro, y nunca
    # se vuelve a evaluar -queda pegado en el valor inicial-; sin `store`
    # se recalcula en cada lectura.
    x_studio_integer_field_Dg6kN = fields.Integer(
        string='New Entero', compute='_compute_x_studio_integer_field_Dg6kN')

    # MIGRACIÓN V19: segunda tanda de campos manuales de Studio (export
    # "Campos (ir.model.fields) (3)"). No se agregan a ninguna vista -eso
    # quedó fuera de alcance de esta tanda-, sólo se formalizan como
    # campos reales para que no se pierdan en el próximo rebuild.
    x_studio_fecha_de_revisin = fields.Date(string='Fecha de revisión')
    x_numero_de_proveedor = fields.Char(string='Número de proveedor (Studio)')
    x_sucursal = fields.Char(string='Sucursal')
    x_solicito = fields.Char(string='Solicitó')
    x_studio_notas = fields.Text(string='Notas')
    x_color = fields.Integer(string='Color')
    x_studio_mkp = fields.Char(string='MKP')
    # MIGRACIÓN V19: campo manual de Studio, nunca formalizado -distinto
    # del `reason` del wizard `account.move.reversal`-.
    reason = fields.Char(string='Motivo')

    # MIGRACIÓN V19: en Studio eran `related=` a través de campos
    # `Many2one` (`reversed_entry_id`/`sale_id`), se mantienen igual.
    x_studio_ref = fields.Char(related='reversed_entry_id.display_name', string='Ref.')
    x_num_pro = fields.Char(related='partner_id.x_num_pro', string='Número de Proveedor', tracking=True)
    x_studio_mkp_1 = fields.Selection(related='sale_id.x_studio_origen_mkp', store=True, string='MKP (origen)')
    x_studio_nombre_del_solicitante = fields.Char(
        related='sale_id.partner_child.name', store=True, string='Nombre del solicitante')
    x_utilidad_venta = fields.Float(related='sale_id.x_utilidad_total', store=True, string='Utilidad venta')
    x_studio_cant_prod_pedido = fields.Integer(
        related='sale_id.cart_quantity', string='Cant. prod. pedido')
    x_studio_utilidad = fields.Float(related='sale_id.x_utilidad_total', string='Utilidad')

    @api.depends('invoice_line_ids')
    def _compute_x_cant_prod_facturados(self):
        for record in self:
            record.x_cant_prod_facturados = sum(record.invoice_line_ids.mapped('quantity'))

    @api.depends('amount_untaxed')
    def _compute_x_costo_total(self):
        for record in self:
            record.x_costo_total = record.amount_untaxed * (1 - studio_get(record, 'x_studio_utilidad') / 100)

    @api.depends('invoice_date')
    def _compute_x_fecha_factura(self):
        for record in self:
            hoy = datetime.date.today()
            array = str(hoy).split('-')
            meses = ["Unknown", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto",
                     "Septiembre", "Octubrer", "Noviembre", "Diciembre"]
            record.x_fecha_factura = "Ciudad de México a " + str(array[2]) + ' de ' + meses[int(array[1])] \
                + " del " + str(array[0])

    @api.depends('amount_residual', 'amount_total')
    def _compute_x_importe_pagado(self):
        for record in self:
            record.x_importe_pagado = record.amount_total - record.amount_residual

    @api.depends('partner_id')
    def _compute_x_studio_auxiliar(self):
        for record in self:
            if record.partner_id:
                record.x_studio_auxiliar = 'P01'
            else:
                record.x_studio_auxiliar = 'mover cliente'

    @api.depends('move_type')
    def _compute_x_tipo_de_comprobante(self):
        for record in self:
            if record.move_type == 'out_invoice':
                record.x_tipo_de_comprobante = 'I – Ingreso'
            elif record.move_type == 'out_refund':
                record.x_tipo_de_comprobante = 'E – Egreso'
            else:
                record.x_tipo_de_comprobante = False

    @api.depends('invoice_line_ids.x_utilidad')
    def _compute_x_utilidad_total(self):
        for record in self:
            record.x_utilidad_total = sum(record.invoice_line_ids.mapped('x_utilidad'))

    # MIGRACIÓN V19: sin `@api.depends` a propósito, ver `common.py`
    # (`x_studio_fecha_de_revisin` no existe en todas las bases).
    def _compute_x_studio_integer_field_Dg6kN(self):
        for record in self:
            record.x_studio_integer_field_Dg6kN = 1


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    x_costo_total = fields.Float(
        string='Costo total', compute='_compute_x_costo_total')
    x_tax_value = fields.Float(
        string='Valor de los impuestos', compute='_compute_x_tax_value')
    x_unit_tax_value = fields.Float(
        string='Impuesto unitario', compute='_compute_x_unit_tax_value')
    x_utilidad = fields.Float(
        string='Utilidad', compute='_compute_x_utilidad', store=True)

    @api.depends('quantity')
    def _compute_x_costo_total(self):
        for record in self:
            record.x_costo_total = studio_get(record, 'x_costo') * record.quantity

    @api.depends('quantity', 'price_subtotal', 'price_total')
    def _compute_x_tax_value(self):
        for record in self:
            if record.quantity > 0:
                record.x_tax_value = record.price_total - record.price_subtotal
            else:
                record.x_tax_value = 0

    @api.depends('price_unit', 'tax_ids')
    def _compute_x_unit_tax_value(self):
        for record in self:
            if record.tax_ids:
                record.x_unit_tax_value = record.price_unit * (record.tax_ids[0].amount / 100)
            else:
                record.x_unit_tax_value = 0.0

    @api.depends('price_unit')
    def _compute_x_utilidad(self):
        for record in self:
            if record.price_unit > 0:
                record.x_utilidad = (record.price_unit - studio_get(record, 'x_costo')) / record.price_unit * 100
            else:
                record.x_utilidad = 0
