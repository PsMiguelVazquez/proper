# -*- coding: utf-8 -*-
from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # MIGRACIÓN V19: sin `store` a propósito (ver `common.py`): sin
    # `@api.depends`, `store=True` sólo calcularía este campo una vez, al
    # crear el registro, y nunca se volvería a evaluar.
    x_estado_documento = fields.Selection(
        [('Documentos entregados', 'Documentos entregados'),
         ('Documentos no entregados', 'Documentos no entregados')],
        string='Estado de documentos', compute='_compute_x_estado_documento')
    x_studio_distancia_1 = fields.Html(
        string='Distancia', compute='_compute_x_studio_distancia_1')
    x_studio_suma_total = fields.Float(
        string='Suma Total', compute='_compute_x_studio_suma_total', store=True)

    # MIGRACIÓN V19: resto de campos manuales de Studio usados por la vista
    # de formulario formalizada (ver `views/stock_picking_form.xml`). Antes
    # sólo vivían como metadatos de Studio (`ir.model.fields` state=manual)
    # y se perdían en cada rebuild de la base; se declaran aquí para que
    # queden versionados junto con el resto del módulo.
    x_studio_motivo = fields.Char(string='Motivo')
    x_documento_entregado = fields.Boolean(string='Documentos entregados')
    x_studio_empleado_validacin_salida = fields.Many2one(
        'hr.employee', string='Responsable de surtido')
    x_studio_salida_de_almacn = fields.Boolean(string='Salida de almacén')
    x_studio_remisin_firmada = fields.Binary(string='Remisión Firmada')
    x_studio_remisin_firmada_filename = fields.Char(string='Nombre de archivo (remisión firmada)')
    x_studio_otros_1 = fields.Binary(string='Otros documentos')
    x_studio_otros_1_filename = fields.Char(string='Nombre de archivo (otros documentos)')
    x_studio_comentarios = fields.Char(string='Comentarios')
    # MIGRACIÓN V19: en Studio eran campos `related` hacia `sale_id`; se
    # mantienen como `related` (con los mismos nombres técnicos que usa la
    # vista) para no duplicar el dato.
    x_studio_estado_de_surtido_de_productos = fields.Selection(
        related='sale_id.x_estado_surtido', store=True, string='Estado de surtido')
    x_documento_entrega_a = fields.Selection(
        related='sale_id.x_doc_entrega', store=True, string='Documentos de entrega')
    x_met_entrega = fields.Selection(
        related='sale_id.x_metodo_entrega', store=True, string='Método de Entrega')
    x_studio_etiquetas = fields.Binary(
        related='sale_id.x_studio_etiquetas', store=True, string='Etiquetas')
    x_studio_orden_de_compra = fields.Binary(
        related='sale_id.x_studio_orden_de_compra', store=True, string='Orden de Compra')
    x_studio_related_field_5mfxb = fields.Text(
        related='sale_id.x_studio_comentarios', store=True, string='Comentarios (pedido de venta)')

    @api.depends('x_documento_entregado')
    def _compute_x_estado_documento(self):
        for record in self:
            if record.x_documento_entregado:
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

    # MIGRACIÓN V19: en Studio era `related='product_id.standard_price'`
    # (no manual); se formaliza igual, lo que además permite depender de él
    # normalmente en `_compute_x_studio_costo_total` en vez del workaround
    # de `studio_get`.
    x_studio_costo_de_compra = fields.Float(
        related='product_id.standard_price', string='Costo de compra')
    x_studio_costo_total = fields.Float(
        string='Costo total', compute='_compute_x_studio_costo_total', store=True)

    # MIGRACIÓN V19: `quantity_done` -> `quantity`.
    @api.depends('quantity', 'x_studio_costo_de_compra')
    def _compute_x_studio_costo_total(self):
        for record in self:
            record.x_studio_costo_total = record.quantity * record.x_studio_costo_de_compra
