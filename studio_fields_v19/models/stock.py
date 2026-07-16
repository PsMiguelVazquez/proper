# -*- coding: utf-8 -*-
from odoo import models, fields, api

from .common import studio_get


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    x_estado_documento = fields.Selection(
        [('Documentos entregados', 'Documentos entregados'),
         ('Documentos no entregados', 'Documentos no entregados')],
        string='Estado de documentos', compute='_compute_x_estado_documento', store=True)
    x_studio_distancia_1 = fields.Html(
        string='Distancia', compute='_compute_x_studio_distancia_1')
    x_studio_suma_total = fields.Float(
        string='Suma Total', compute='_compute_x_studio_suma_total', store=True)

    # MIGRACIÓN V19: sin `@api.depends` a propósito, ver `common.py`
    # (`x_documento_entregado` no existe en todas las bases).
    def _compute_x_estado_documento(self):
        for record in self:
            if studio_get(record, 'x_documento_entregado', False):
                record.x_estado_documento = 'Documentos entregados'
            else:
                record.x_estado_documento = 'Documentos no entregados'

    @api.depends('partner_id')
    def _compute_x_studio_distancia_1(self):
        for record in self:
            record.x_studio_distancia_1 = (
                "<a href='https://www.google.com/maps/dir/" + str(record.l10n_mx_edi_src_lat) + ",+"
                + str(record.l10n_mx_edi_src_lon) + "/" + str(record.l10n_mx_edi_des_lat) + ","
                + str(record.l10n_mx_edi_des_lon)
                + "/@25.66,-100.37,4.88z/data=!4m8!4m7!1m5!1m1!1s0x0:0x78eab5480bf3fb6f!2m2!1d-99.1620065"
                + "!2d19.4958859!1m0' target='_blank' > Ruta</a>"
            )

    # MIGRACIÓN V19: `move_ids_without_package` -> `move_ids`.
    @api.depends('move_ids.x_studio_costo_total')
    def _compute_x_studio_suma_total(self):
        for record in self:
            record.x_studio_suma_total = sum(record.move_ids.mapped('x_studio_costo_total'))


class StockMove(models.Model):
    _inherit = 'stock.move'

    x_studio_costo_total = fields.Float(
        string='Costo total', compute='_compute_x_studio_costo_total', store=True)

    # MIGRACIÓN V19: `quantity_done` -> `quantity`. Sin `x_studio_costo_de_compra`
    # en `@api.depends` a propósito, ver `common.py`.
    @api.depends('quantity')
    def _compute_x_studio_costo_total(self):
        for record in self:
            record.x_studio_costo_total = record.quantity * studio_get(record, 'x_studio_costo_de_compra')
