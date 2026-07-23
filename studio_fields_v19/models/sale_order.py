# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: campos calculados creados originalmente con Odoo Studio,
formalizados aquí como código. Ver `__manifest__.py` para el detalle de qué
se excluyó (subsistema de Requerimientos/Propuestas de compra).
"""
from odoo import models, fields, api

from .common import studio_get


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_studio_cant_asignada = fields.Integer(
        string='Cant. Asignada', compute='_compute_x_studio_cant_asignada')
    x_studio_cant_entregada = fields.Integer(
        string='Cant. Entregada', compute='_compute_x_studio_cant_entregada')
    x_studio_cant_x_entregar = fields.Integer(
        string='Cant. x Entregar', compute='_compute_x_studio_cant_x_entregar')
    x_sale_id_stock_picking_count = fields.Integer(
        string='Sales Order count', compute='_compute_x_sale_id_stock_picking_count')
    # MIGRACIÓN V19: se mantiene además del anterior porque ambos existían
    # como campos de Studio independientes (el original de `x_sale` usaba un
    # nombre de campo `sale` que nunca existió en `stock.picking` -siempre
    # fue `sale_id`-, por lo que ya fallaba antes de esta migración).
    x_sale__stock_picking_count = fields.Integer(
        string='Sale count', compute='_compute_x_sale__stock_picking_count')
    x_utilidad_total = fields.Float(
        string='Utilidad %', compute='_compute_x_utilidad_total')
    x_utilidad_total_por = fields.Integer(
        string='Utilidad total%', compute='_compute_x_utilidad_total_por', store=True)
    # MIGRACIÓN V19: campo sin uso detectado en el resto del código (etiqueta
    # de Studio "New Texto" sin renombrar); se formaliza igual para no
    # perder los valores ya guardados en producción.
    x_studio_char_field_5mFSv = fields.Char(
        string='New Texto', compute='_compute_x_studio_char_field_5mFSv', store=True)
    x_studio_pedido = fields.Boolean(
        string='pedido', compute='_compute_x_studio_pedido', store=True)

    # MIGRACIÓN V19: campos manuales de Studio (no calculados) usados desde
    # `stock.picking` vía `related=` en la vista formalizada del formulario
    # de traslado (`stock.py`). Se declaran aquí, igual que en Studio, para
    # que sobrevivan a un rebuild de la base (Studio los perdería).
    x_doc_entrega = fields.Selection(
        [('factura', 'Factura'),
         ('remision_sin_costo', 'Remisión sin costo'),
         ('remision_con_costo', 'Remisión con costo')],
        string='Documentos de entrega', tracking=True)
    x_estado_surtido = fields.Selection(
        [('pendiente', 'Pendiente'), ('surtir', 'Surtir')],
        string='Estado de surtido')
    x_metodo_entrega = fields.Selection(
        [('flotilla', 'Flotilla'), ('paqueteria', 'Paqueteria'),
         ('recolecta', 'Recolecta'), ('Foráneo', 'Foráneo')],
        string='Método de entrega')
    x_otros_documentos = fields.Many2many('ir.attachment', string='Otros documentos', tracking=True)
    x_studio_comentarios = fields.Text(string='Comentarios')
    x_studio_etiquetas = fields.Binary(string='Etiquetas')
    x_studio_orden_de_compra = fields.Binary(string='Orden de Compra')

    # MIGRACIÓN V19: campos manuales de Studio usados por las listas
    # formalizadas de "Cotizaciones por aprobar"/"Pedidos de
    # ventas"/"Marketplace" (ver `views/sale_order_list_*.xml`).
    x_aprovacion_compras = fields.Boolean(string='Aprovacion Compras')
    x_studio_almacn = fields.Char(related='warehouse_id.name', string='Almacén')
    x_studio_n_orden_de_compra = fields.Char(string='N° Orden de compra', tracking=True)
    x_studio_origen_mkp = fields.Selection(
        [('AMAZON', 'AMAZON'), ('MERCADO LIBRE', 'MERCADO LIBRE'), ('LIVERPOOL', 'LIVERPOOL'),
         ('LINIO', 'LINIO'), ('CLARO SHOP', 'CLARO SHOP'), ('ELENAS', 'ELENAS'),
         ('WALMART', 'WALMART'), ('SEARS', 'SEARS'), ('SHEIN', 'SHEIN'),
         ('SANBORNS', 'SAMBORNS'), ('COPPEL', 'COPPEL'), ('ELEKTRA', 'ELEKTRA'),
         ('FARMACIAS DEL AHORRO', 'FARMACIAS DEL AHORRO')],
        string='Origen MKP')
    x_studio_referencia_de_venta_marketplace = fields.Char(string='Referencia de venta Marketplace')
    x_studio_venta_mostrador = fields.Boolean(string='Venta Mostrador')
    # MIGRACIÓN V19: en Studio era `related='albaran.state'`; `albaran` es
    # `Many2one`, así que se mantiene igual.
    x_estado_almacen = fields.Selection(
        related='albaran.state', store=True, string='Estado de almacén de entrega')
    # MIGRACIÓN V19: en Studio eran `related='purchase_ids.state'`/
    # `related='invoice_ids.state'`, pero `purchase_ids`/`invoice_ids` son
    # `Many2many` (puede haber más de una compra/factura por pedido) y
    # `related=` no soporta atravesar relaciones x2many; se reescriben como
    # compute tomando el estado del primer registro vinculado.
    x_estado_compra = fields.Selection(
        [('draft', 'RFQ'), ('sent', 'RFQ Sent'), ('to approve', 'To Approve'),
         ('purchase', 'Purchase Order'), ('cancel', 'Cancelled'), ('consolidate', 'Consolidada')],
        string='Estado de compras', compute='_compute_x_estado_compra', store=True, tracking=True)
    x_estado_factura = fields.Selection(
        [('draft', 'Draft'), ('posted', 'Posted'), ('cancel', 'Cancelled')],
        string='Estado de Facturación', compute='_compute_x_estado_factura', store=True)
    # MIGRACIÓN V19: en Studio era `related='purchase_ids.picking_ids.state'`
    # (estado del traslado de entrada asociado a las órdenes de compra
    # generadas para este pedido); `purchase_ids` y `picking_ids` son ambos
    # x2many, y `related=` no soporta atravesar dos saltos x2many seguidos
    # (mismo caso que `x_estado_compra`/`x_status_surtido` en esta misma
    # clase), así que nunca se había formalizado. Se reescribe como compute
    # tomando el estado del primer traslado, mismas opciones que
    # `stock.picking.state` (igual que `x_status_surtido`).
    x_state = fields.Selection(
        [('draft', 'Draft'), ('waiting', 'Waiting Another Move'), ('confirmed', 'Waiting Availability'),
         ('assigned', 'Ready'), ('done', 'Done'), ('cancel', 'Cancelled')],
        string='Estado Almacén', compute='_compute_x_state', tracking=True)

    @api.depends('purchase_ids.state')
    def _compute_x_estado_compra(self):
        for record in self:
            record.x_estado_compra = record.purchase_ids[:1].state

    @api.depends('invoice_ids.state')
    def _compute_x_estado_factura(self):
        for record in self:
            record.x_estado_factura = record.invoice_ids[:1].state

    @api.depends('purchase_ids.picking_ids.state')
    def _compute_x_state(self):
        for record in self:
            record.x_state = record.purchase_ids.picking_ids[:1].state

    @api.depends('order_line.cantidad_asignada')
    def _compute_x_studio_cant_asignada(self):
        for record in self:
            record.x_studio_cant_asignada = sum(record.order_line.mapped('cantidad_asignada'))

    @api.depends('order_line.qty_delivered')
    def _compute_x_studio_cant_entregada(self):
        for record in self:
            record.x_studio_cant_entregada = sum(record.order_line.mapped('qty_delivered'))

    @api.depends('order_line.qty_to_deliver')
    def _compute_x_studio_cant_x_entregar(self):
        for record in self:
            record.x_studio_cant_x_entregar = sum(record.order_line.mapped('qty_to_deliver'))

    def _compute_x_sale_id_stock_picking_count(self):
        # MIGRACIÓN V19: el botón inteligente "ALM14" (ver
        # `novu_sale_order/views/sale_order_view.xml`) debe contar sólo los
        # traslados de la venta que pertenecen específicamente al almacén
        # ALM14 (código de `stock.warehouse`, nombre real "MARKETPLACE"),
        # no todos los traslados de la venta -contaba sin filtrar por
        # almacén, dando de alta un número que no coincidía con lo que
        # mostraba V15 para el mismo pedido-.
        for record in self:
            record.x_sale_id_stock_picking_count = self.env['stock.picking'].search_count([
                ('sale_id', '=', record.id),
                ('warehouse_id.code', '=', 'ALM14'),
            ])

    def _compute_x_sale__stock_picking_count(self):
        # MIGRACIÓN V19: el original agrupaba con `read_group` sobre un
        # campo `sale` inexistente en `stock.picking` (siempre fue
        # `sale_id`) y además usaba la firma antigua de `read_group`
        # (diccionarios con clave `<campo>_count`), incompatible con esta
        # versión. Se reescribe con `search_count`, igual que el campo
        # gemelo `x_sale_id_stock_picking_count`.
        for record in self:
            record.x_sale__stock_picking_count = self.env['stock.picking'].search_count(
                [('sale_id', '=', record.id)])

    @api.depends('order_line.x_utilidad')
    def _compute_x_utilidad_total(self):
        for record in self:
            ol = record.order_line.filtered(lambda x: x.product_uom_qty > 0)
            record.x_utilidad_total = sum(ol.mapped('x_utilidad')) / len(ol) if ol else 0

    @api.depends('order_line.x_utilidad_por')
    def _compute_x_utilidad_total_por(self):
        for record in self:
            record.x_utilidad_total_por = sum(record.order_line.mapped('x_utilidad_por'))

    @api.depends('partner_id')
    def _compute_x_studio_char_field_5mFSv(self):
        for record in self:
            record.x_studio_char_field_5mFSv = _fecha_larga_cdmx()

    # MIGRACIÓN V19: `order_line.x_pedido` ya está formalizado más abajo, en
    # `SaleOrderLine`, así que ya no hace falta el workaround `studio_get`.
    @api.depends('order_line.x_pedido')
    def _compute_x_studio_pedido(self):
        for record in self:
            pedidos = record.order_line.mapped('x_pedido')
            record.x_studio_pedido = False if False in pedidos else True

    # MIGRACIÓN V19: segunda tanda de campos manuales de Studio (export
    # "Campos (ir.model.fields) (3)"). No incluye `x_req_line`,
    # `x_req_line_compras`, `x_lines_requirements`, `x_lines_proposa` ni
    # `x_progreso_requerimiento` -subsistema de Requerimientos/Propuestas,
    # fuera de alcance, ver descripción del manifest-.
    x_studio_many2one_field_K1t0z = fields.Many2one('crm.lead', string='Lead/Oportunidad')
    x_folio = fields.Char(string='Folio')
    x_tipo_de_articulos = fields.Char(string='Tipo de artículos')
    x_Empresa = fields.Char(string='Empresa')
    x_motivo_rechazo = fields.Text(string='Motivo de rechazo', tracking=True)
    x_orden_compra = fields.Many2one('purchase.order', string='Orden de compra')
    x_studio_flotilla = fields.Boolean(string='Flotilla')
    x_studio_recolecta = fields.Boolean(string='Recolecta')
    x_studio_solicit = fields.Many2one('res.partner', string='Solicitó')
    x_studio_estado_de_validacin = fields.Selection(
        [('1', 'Contado'), ('2', 'Excede credito'), ('3', 'Falta información'), ('4', 'Facturas vencidas')],
        string='Estado de validación')
    x_no_guia_ventas = fields.Char(string='N° de guía', tracking=True)
    x_studio_paquetera = fields.Boolean(string='Paquetería')
    x_studio_many2many_field_yXYzo = fields.Many2many('stock.picking.type', string='Tipo de albarán')
    x_studio_factura_timbrada = fields.Binary(string='Factura Timbrada')
    x_studio_factura_timbrada_filename = fields.Char(string='Nombre de archivo (factura timbrada)')
    x_studio_remisin = fields.Binary(string='Remisión')
    x_studio_remisin_filename = fields.Char(string='Nombre de archivo (remisión)')
    x_studio_remisin_ciega = fields.Binary(string='Remisión Ciega')
    x_studio_remisin_ciega_filename = fields.Char(string='Nombre de archivo (remisión ciega)')
    x_studio_etiquetas_filename = fields.Char(string='Nombre de archivo (etiquetas)')
    x_studio_orden_de_compra_filename = fields.Char(string='Nombre de archivo (orden de compra)')
    x_studio_otros_filename = fields.Char(string='Nombre de archivo (otros)')
    x_studio_many2many_field_ghmoC = fields.Many2many(
        'stock.picking', 'sale_order_stock_picking_ghmoC_rel', string='Albarán')
    x_studio_many2many_field_ma4cB = fields.Many2many(
        'stock.picking', 'sale_order_stock_picking_ma4cB_rel', string='Albarán (2)')
    x_studio_con_tiempo_de_entrega = fields.Boolean(string='Con tiempo de entrega')
    x_mot_canc_comer = fields.Text(string='Motivo de cancelación del comercial', tracking=True)
    x_requiere_factura = fields.Selection([('SI', 'SI'), ('NO', 'NO')], string='Requiere factura', tracking=True)
    x_studio_remisin_1 = fields.Boolean(string='Remisión (marcada)')
    x_studio_remisin_ciega_1 = fields.Boolean(string='Remisión Ciega (marcada)')
    x_studio_factura_timbrada_1 = fields.Boolean(string='Factura Timbrada (marcada)')
    x_studio_otros = fields.Binary(string='Otros documentos (archivo)')
    x_fecha_devolucion = fields.Date(string='Fecha Devolución', tracking=True)
    # MIGRACIÓN V19: `x_fecha_factura` (sale.order, no confundir con el
    # `x_fecha_factura` de `account.move`, ya formalizado) nunca se había
    # formalizado; `novu_sale_order/views/sale_order_view.xml` ya lo
    # referenciaba directamente.
    x_fecha_factura = fields.Datetime(string='Fecha de Facturación', tracking=True)
    x_es_muestra = fields.Boolean(string='Es Muestra', tracking=True)
    x_moti_cancel_comp = fields.Char(string='Motivo de rechazo de cancelación', tracking=True)
    x_acep_cancel_compra = fields.Boolean(string='Aceptar cancelación de venta', tracking=True)

    # MIGRACIÓN V19: en Studio eran `related=` a través de campos
    # `Many2one` (`partner_id`/`albaran`), se mantienen igual.
    x_studio_holding_1 = fields.Char(
        related='partner_id.parent_id.x_holding.display_name', string='Holding')
    x_studio_empresa = fields.Char(related='partner_id.parent_id.name', string='Empresa (relación)')
    x_studio_holding_2 = fields.Char(related='partner_id.x_holding.name', string='Holding (2)')
    x_studio_n_de_gua = fields.Char(related='albaran.x_studio_n_de_gua', string='N° de guía (albarán)')
    x_studio_n_de_gua_1 = fields.Char(related='albaran.x_studio_n_de_gua', string='N° de guía (2)')
    x_studio_grupo = fields.Char(related='partner_id.x_grupo_cliente.x_name', string='Grupo')
    x_studio_plazo_de_pago = fields.Char(
        related='partner_id.property_payment_term_id.display_name', string='Política de pago')
    x_fecha_surtido = fields.Datetime(related='albaran.scheduled_date', string='Fecha de surtido')
    x_studio_rfc = fields.Char(related='partner_id.vat', string='RFC')
    # MIGRACIÓN V19: `x_num_pro` (sale.order) nunca se había formalizado;
    # `novu_sale_order/views/sale_order_view.xml` ya lo referenciaba
    # directamente, causando 'Field "x_num_pro" does not exist in model
    # "sale.order"'.
    x_num_pro = fields.Char(related='partner_id.x_num_pro', string='Número de Proveedor', tracking=True)

    # MIGRACIÓN V19: en Studio era `related='partner_id.x_area'`, pero
    # `x_area` en `res.partner` es a su vez un compute (toma la primera
    # oportunidad vinculada, ver `res_partner.py`); un `related=` normal
    # funciona igual aquí porque el salto sigue siendo `Many2one`
    # (`partner_id`).
    x_area = fields.Char(related='partner_id.x_area', string='Área', tracking=True)

    # MIGRACIÓN V19: en Studio era `related='picking_ids.state'`, pero
    # `picking_ids` es `One2many`/`Many2many` (puede haber más de un
    # traslado por pedido) y `related=` no soporta atravesar x2many (mismo
    # caso que `x_estado_compra` en esta misma clase); se reescribe como
    # compute tomando el estado del primer traslado.
    x_status_surtido = fields.Selection(
        [('draft', 'Draft'), ('waiting', 'Waiting Another Move'), ('confirmed', 'Waiting Availability'),
         ('assigned', 'Ready'), ('done', 'Done'), ('cancel', 'Cancelled')],
        string='*Estado de surtido', compute='_compute_x_status_surtido', tracking=True)

    @api.depends('picking_ids.state')
    def _compute_x_status_surtido(self):
        for record in self:
            record.x_status_surtido = record.picking_ids[:1].state


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # MIGRACIÓN V19: segunda tanda de campos manuales de Studio. `x_pedido`
    # ya se usaba desde `_compute_x_studio_pedido` (arriba, en `SaleOrder`)
    # a través de `studio_get()` porque todavía no era un campo real; ahora
    # que se formaliza aquí, ya se puede depender de él normalmente.
    x_sol_atendido = fields.Boolean(string='Solicitud atendida')
    x_studio_cantidad_disponible = fields.Integer(string='Cantidad disponible')
    x_studio_modelo_1 = fields.Char(string='Modelo (texto)')
    x_dias_habiles = fields.Text(string='Días hábiles')
    x_pedido = fields.Boolean(string='pedido')
    x_costo_envio = fields.Monetary(string='Costo de envío (Studio)')

    # MIGRACIÓN V19: en Studio eran `related=` a través de campos
    # `Many2one` (`product_id`/`product_template_id`/`order_id`), se
    # mantienen igual.
    x_studio_cdigo_de_barras = fields.Char(related='product_id.barcode', store=True, string='Código de barras')
    x_studio_modelo = fields.Char(
        related='product_id.x_studio_many2one_field_AqNlU.x_name', store=True, string='Modelo')
    x_studio_cdigo_sat = fields.Many2one(
        'product.unspsc.code', related='product_id.unspsc_code_id', string='Código SAT')
    x_studio_related_field_10QsN = fields.Selection(
        related='product_template_id.invoice_policy', store=True, string='New Campo relacionado')
    x_modelo_producto = fields.Char(related='product_id.default_code', store=True, string='Modelo producto')
    x_studio_descripcin_comercial = fields.Text(
        related='product_id.description_sale', string='Descripción comercial')
    x_studio_estado_del_pedido = fields.Selection(
        related='order_id.state', store=True, string='Estado del pedido')
    x_ultimo_precio_compra = fields.Float(
        related='product_template_id.ultimo_costo_compra', store=True, string='Último precio de compra')
    x_studio_categoria_del_producto = fields.Char(
        related='product_template_id.categ_id.name', store=True, string='Categoría del producto')
    x_numcliente = fields.Char(
        related='order_id.partner_id.x_num_cliente', store=True, string='N° cliente')
    x_studio_familia = fields.Char(
        related='product_template_id.x_studio_many2one_field_RWuq7.display_name', string='Familia')
    x_fabricante_producto = fields.Char(
        related='product_template_id.x_fabricante.display_name', store=True, string='Fabricante')
    x_grupo_producto = fields.Char(
        related='product_template_id.x_studio_many2one_field_0X3u9.display_name', store=True, string='Grupo')
    x_linea_producto = fields.Char(
        related='product_template_id.x_studio_many2one_field_LZOP8.display_name', store=True, string='Línea')
    x_fecha_pedido = fields.Datetime(related='order_id.date_order', store=True, string='Fecha de pedido')

    x_comision = fields.Monetary(
        string='Comisión (Studio)', compute='_compute_x_comision', store=True)
    x_invoiced_subtotal = fields.Float(
        string='Subtotal facturado', compute='_compute_x_invoiced_subtotal')
    x_por_surtir = fields.Float(
        string='Por Surtir', compute='_compute_x_por_surtir', store=True)
    x_precio_iva = fields.Float(
        string='Precio + IVA', compute='_compute_x_precio_iva', store=True)
    x_subtotal_iva = fields.Float(
        string='Subtotal + IVA', compute='_compute_x_subtotal_iva', store=True)
    x_utilidad = fields.Float(
        string='Utilidad % (Studio)', compute='_compute_x_utilidad', store=True)
    # MIGRACIÓN V19: usa ubicaciones de almacén (`location_id`) fijas por id
    # (187 y 80), copiadas tal cual del cálculo original de Studio. Esos ids
    # son específicos de la base de datos de producción de origen; hay que
    # verificar que sigan siendo válidos en la base de destino antes de usar
    # este campo. Se declara `Html` (el export de Studio decía "Carácter",
    # pero el compute arma una `<table>`; con `Char` un `widget="html"` no
    # la renderiza en v19 -mismo bug encontrado en `existencia`/`x_detalle`
    # de `sale_purchase_confirm`-).
    x_studio_disponible = fields.Html(
        string='Disponible', compute='_compute_x_studio_disponible', store=True)

    @api.depends('price_unit', 'comision')
    def _compute_x_comision(self):
        for record in self:
            record.x_comision = record.price_unit * record.comision

    @api.depends('qty_invoiced', 'price_unit')
    def _compute_x_invoiced_subtotal(self):
        for record in self:
            record.x_invoiced_subtotal = record.qty_invoiced * record.price_unit

    # MIGRACIÓN V19: sin `x_Reservado` en `@api.depends` a propósito, ver
    # `common.py` (no existe en todas las bases).
    @api.depends('product_uom_qty', 'qty_delivered')
    def _compute_x_por_surtir(self):
        for record in self:
            if record.qty_delivered == 0:
                record.x_por_surtir = record.product_uom_qty - studio_get(record, 'x_Reservado')
            else:
                record.x_por_surtir = record.product_uom_qty - record.qty_delivered

    @api.depends('price_unit')
    def _compute_x_precio_iva(self):
        for record in self:
            record.x_precio_iva = record.price_unit * .16 + record.price_unit

    @api.depends('x_precio_iva', 'product_uom_qty')
    def _compute_x_subtotal_iva(self):
        for record in self:
            record.x_subtotal_iva = record.x_precio_iva * record.product_uom_qty

    @api.depends('price_unit', 'x_studio_costo_promedio')
    def _compute_x_utilidad(self):
        for record in self:
            if record.price_unit > 0:
                record.x_utilidad = (1 - (record.x_studio_costo_promedio / record.price_unit)) * 100
            else:
                record.x_utilidad = 0

    @api.depends('product_id')
    def _compute_x_studio_disponible(self):
        for record in self:
            quants = record.product_id.stock_quant_ids
            zero = sum(quants.filtered(lambda x: x.location_id.id == 187).mapped('available_quantity'))
            zero1 = sum(quants.filtered(lambda x: x.location_id.id == 187).mapped('reserved_quantity'))
            market = sum(quants.filtered(lambda x: x.location_id.id == 80).mapped('available_quantity'))
            market1 = sum(quants.filtered(lambda x: x.location_id.id == 80).mapped('reserved_quantity'))
            record.x_studio_disponible = (
                "<table><thead><tr><th>A-0</th><th>A14</th></tr><tr><th>D/R</th><th>D/R</th></tr></thead>"
                "<tbody><tr><td>" + str(zero) + "/" + str(zero1) + "</td><td>" + str(market) + "/" + str(market1)
                + "</td></tr></tbody>"
            )


def _fecha_larga_cdmx():
    import datetime
    hoy = datetime.date.today()
    array = str(hoy).split('-')
    meses = ["Unknown", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto",
             "Septiembre", "Octubrer", "Noviembre", "Diciembre"]
    return "Ciudad de México a " + str(array[2]) + ' de ' + meses[int(array[1])] + " del " + str(array[0])
