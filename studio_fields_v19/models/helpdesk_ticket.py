# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    # MIGRACIÓN V19: campos manuales de Studio (export "Campos
    # (ir.model.fields) (3)"). No se agregan a ninguna vista -eso quedó
    # fuera de alcance de esta tanda-, sólo se formalizan como campos
    # reales para que no se pierdan en el próximo rebuild.
    x_studio_vencimiento_de_la_garanta = fields.Date(string='Vencimiento de la garantía')
    x_studio_cantidad = fields.Integer(string='Cantidad')
    x_studio_evidencia = fields.Binary(string='Evidencia')
    x_studio_evidencia_filename = fields.Char(string='Nombre de archivo (evidencia)')

    # MIGRACIÓN V19: en Studio eran `related=` a través de `sale_order_id`
    # (`Many2one`), se mantienen igual.
    x_studio_fecha_de_surtido_1 = fields.Datetime(
        related='sale_order_id.x_fecha_surtido', store=True, string='Fecha de surtido')
    x_studio_fecha_de_surtido = fields.Datetime(
        related='sale_order_id.commitment_date', store=True, string='Fecha de surtido')

    # MIGRACIÓN V19: en Studio era `related='sale_order_id.invoice_ids.name'`
    # -último salto `Many2many`, no soportado por `related=`-; se reescribe
    # como compute tomando la primera factura.
    x_studio_factura = fields.Char(string='Factura', compute='_compute_x_studio_factura')

    @api.depends('sale_order_id.invoice_ids.name')
    def _compute_x_studio_factura(self):
        for record in self:
            record.x_studio_factura = record.sale_order_id.invoice_ids[:1].name
