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

    # MIGRACIÓN V19: segunda tanda de campos manuales de Studio (export
    # "Campos (ir.model.fields) (3)"). No incluye `x_studio_otros_documentos_1`
    # (related cruzando un many2many, mismo problema ya documentado antes en
    # este archivo) ni `x_studio_binary_field_U2SJO_filename` (nombre de
    # archivo huérfano: el campo binario que acompañaba,
    # `x_studio_binary_field_U2SJO`, se eliminó por no tener ningún uso, ver
    # `__init__.py`).
    x_studio_many2one_field_RiLKk = fields.Many2one('stock.picking', string='Albarán')
    x_studio_n_de_gua = fields.Char(string='N° de guía')
    x_studio_empleado_solicitante = fields.Many2one('hr.employee', string='Empleado Solicitante')
    x_studio_empleado_validacin_entrada = fields.Many2one('hr.employee', string='Empleado validación entrada')
    x_studio_entrada_de_almacn = fields.Boolean(string='Entrada de almacén')
    x_studio_many2one_field_uXDXF = fields.Many2one('sale.order', string='Pedido de venta')

    # MIGRACIÓN V19: en Studio eran `related=` hacia `sale_id` (`Many2one`),
    # se mantienen igual.
    x_studio_productos = fields.One2many(
        'sale.order.line', related='sale_id.order_line', string='Productos')
    x_studio_flotilla = fields.Boolean(
        related='sale_id.x_studio_flotilla', store=True, string='Flotilla')
    x_studio_fecha_de_surtido = fields.Datetime(
        related='sale_id.x_fecha_surtido', store=True, string='Fecha de surtido')
    x_no_guia_alm = fields.Char(related='sale_id.x_no_guia_ventas', store=True, string='N° de guía')
    x_studio_remisin_ciega = fields.Binary(
        related='sale_id.x_studio_remisin_ciega', store=True, string='Remisión Ciega')
    x_studio_remisin = fields.Binary(related='sale_id.x_studio_remisin', store=True, string='Remisión')
    x_studio_factura_timbrada = fields.Binary(
        related='sale_id.x_studio_factura_timbrada', store=True, string='Factura Timbrada')
    x_studio_otros = fields.Binary(related='sale_id.x_studio_otros', store=True, string='Otros')
    x_studio_paquetera = fields.Boolean(
        related='sale_id.x_studio_paquetera', store=True, string='Paquetería')
    x_studio_recolecta = fields.Boolean(
        related='sale_id.x_studio_recolecta', store=True, string='Recolecta')
    x_studio_remisin_1 = fields.Binary(related='sale_id.x_studio_remisin', store=True, string='Remisión')
    x_studio_factura_timbrada_1 = fields.Boolean(
        related='sale_id.x_studio_factura_timbrada_1', store=True, string='Factura Timbrada')
    x_studio_remisin_ciega_1 = fields.Boolean(
        related='sale_id.x_studio_remisin_ciega_1', store=True, string='Remisión Ciega')
    x_studio_remisin_2 = fields.Boolean(
        related='sale_id.x_studio_remisin_1', store=True, string='Remisión')
    # MIGRACIÓN V19: en Studio era `related='sale.invoice_status'`, pero
    # `sale` nunca existió como campo de `stock.picking` (siempre fue
    # `sale_id`, mismo error ya documentado en `x_sale__stock_picking_count`
    # en `sale_order.py`).
    x_studio_estado_de_factura = fields.Selection(
        related='sale_id.invoice_status', store=True, string='Estado de factura')

    # MIGRACIÓN V19: `x_studio_many2one_field_vOr3z` (Grupo de
    # abastecimiento, `related='move_lines.group_id'` en Studio) no se
    # formaliza: el modelo `procurement.group` que usaba ya no existe en
    # v19 (el concepto de "grupo de abastecimiento" se reestructuró por
    # completo en versiones más recientes del core), y `stock.move` ya no
    # tiene un campo `group_id` del que depender.

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

    # MIGRACIÓN V19: segunda tanda de campos manuales de Studio.
    x_sale_id = fields.Many2one('sale.order', string='Sale ID')
    x_studio_many2one_field_ViMUw = fields.Many2one('x_estado_del_producto', string='Estado del producto')
    x_studio_many2one_field_x7d2A = fields.Many2one('account.move', string='Asiento contable')
    # MIGRACIÓN V19: en Studio era `related='sale_line_id.order_id.invoice_ids'`
    # -tres saltos, el último (`invoice_ids`) `Many2many`-, no soportado por
    # `related=`; se reescribe como compute.
    x_studio_factura = fields.Many2many(
        'account.move', 'stock_move_invoice_ids_rel', string='Factura', compute='_compute_x_studio_factura')

    @api.depends('sale_line_id.order_id.invoice_ids')
    def _compute_x_studio_factura(self):
        for record in self:
            record.x_studio_factura = record.sale_line_id.order_id.invoice_ids


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    # MIGRACIÓN V19: en Studio eran `related=` a través de campos
    # `Many2one` (`picking_id`/`product_id`), se mantienen igual.
    x_agente_ventas = fields.Char(
        related='picking_id.sale_id.create_uid.name', store=True, string='Agente ventas')
    x_studio_many2one_field_Qp3X9 = fields.Many2one('x_estado_del_producto', string='Estado del producto')
    # MIGRACIÓN V19: sin `store=True` -a diferencia del resto de los
    # `related=` de este archivo- porque `standard_price` es
    # `company_dependent=True` en 19.0 (se guarda internamente como jsonb
    # por compañía); Odoo no puede copiar ese valor directo a una columna
    # `Float` normal al declarar el `related` como almacenado.
    x_costo_promedio = fields.Float(related='product_id.standard_price', string='Costo promedio')
    x_studio_referencia_interna = fields.Char(
        related='product_id.default_code', store=True, string='Referencia interna')
    x_studio_cantidad_total_disponible = fields.Float(
        related='product_id.free_qty', string='Cantidad total disponible')
    x_studio_cantidad_disponible_almacn_0 = fields.Float(
        related='product_id.stock_quant_warehouse_zero', string='Cantidad disponible almacén 0')


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    # MIGRACIÓN V19: en Studio eran `related='product_id...'` (`Many2one`).
    x_studio_producto = fields.Char(related='product_id.name', string='Producto')
    x_studio_precio_de_venta = fields.Float(related='product_id.list_price', string='Precio de venta')
    x_studio_cantidad_reservada = fields.Float(
        related='product_id.outgoing_qty', string='Cantidad reservada')
    x_studio_modelo_del_producto = fields.Char(
        related='product_id.default_code', store=True, string='Modelo del producto')
    x_studio_cdigo_de_barras = fields.Char(
        related='product_id.barcode', store=True, string='Código de barras')
    x_studio_clave_sat = fields.Char(
        related='product_id.unspsc_code_id.code', store=True, string='Clave SAT')
    x_studio_fabricante = fields.Char(
        related='product_id.x_fabricante.x_name', store=True, string='Fabricante')


class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    # MIGRACIÓN V19: en Studio era `related='product_id.x_fabricante'`
    # (`Many2one`), se mantiene igual.
    x_studio_marca = fields.Many2one('x_fabricante', related='product_id.x_fabricante', string='Marca')


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    x_studio_rea = fields.Char(string='Área')
