# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    x_studio_costo_total = fields.Float(
        string='Importe entregado', compute='_compute_x_studio_costo_total', store=True)
    x_studio_descuento = fields.Float(string='Descuento')

    @api.depends('price_unit', 'qty_received')
    def _compute_x_studio_costo_total(self):
        for record in self:
            record.x_studio_costo_total = record.qty_received * record.price_unit


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    x_suma_costo_total = fields.Float(
        string='Suma', compute='_compute_x_suma_costo_total', store=True)

    # MIGRACIÓN V19: segunda tanda de campos manuales de Studio (export
    # "Campos (ir.model.fields) (3)"). `x_studio_nmero_de_factura` ya se
    # referenciaba desde el módulo `novu_purchase_order` sin existir como
    # campo real -bug detectado en una ronda anterior, queda resuelto al
    # formalizarlo aquí-.
    x_studio_recoger_en = fields.Text(string='Recoger en')
    x_studio_observaciones = fields.Text(string='Observaciones')
    x_studio_atencin = fields.Text(string='Atención')
    x_studio_nmero_de_factura = fields.Char(string='Número de factura')
    # MIGRACIÓN V19: en Studio era `related='date_planned'` -sin punto,
    # apunta a otro campo del mismo modelo-, se mantiene igual.
    x_studio_datetime_field_oVVvK = fields.Datetime(related='date_planned', string='New Fecha y hora')

    @api.depends('order_line.x_studio_costo_total')
    def _compute_x_suma_costo_total(self):
        for record in self:
            record.x_suma_costo_total = sum(record.order_line.mapped('x_studio_costo_total'))
