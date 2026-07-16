# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, api


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
    # preserva tal cual para no perder los datos ya guardados.
    x_studio_integer_field_Dg6kN = fields.Integer(
        string='New Entero', compute='_compute_x_studio_integer_field_Dg6kN', store=True)

    @api.depends('invoice_line_ids')
    def _compute_x_cant_prod_facturados(self):
        for record in self:
            record.x_cant_prod_facturados = sum(record.invoice_line_ids.mapped('quantity'))

    @api.depends('amount_untaxed', 'x_studio_utilidad')
    def _compute_x_costo_total(self):
        for record in self:
            record.x_costo_total = record.amount_untaxed * (1 - record.x_studio_utilidad / 100)

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

    @api.depends('x_studio_fecha_de_revisin')
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

    @api.depends('x_costo', 'quantity')
    def _compute_x_costo_total(self):
        for record in self:
            record.x_costo_total = record.x_costo * record.quantity

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

    @api.depends('x_costo', 'price_unit')
    def _compute_x_utilidad(self):
        for record in self:
            if record.price_unit > 0:
                record.x_utilidad = (record.price_unit - record.x_costo) / record.price_unit * 100
            else:
                record.x_utilidad = 0
