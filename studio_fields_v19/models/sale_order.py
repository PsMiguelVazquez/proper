# -*- coding: utf-8 -*-
"""
MIGRACIÓN V19: campos calculados creados originalmente con Odoo Studio,
formalizados aquí como código. Ver `__manifest__.py` para el detalle de qué
se excluyó (subsistema de Requerimientos/Propuestas de compra).
"""
from odoo import models, fields, api


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
    # MIGRACIÓN V19: depende de `order_line.x_pedido`, campo que sigue
    # viviendo únicamente como columna de Odoo Studio (no formalizado en
    # código); se referencia de forma dinámica, funciona igual que antes.
    x_studio_pedido = fields.Boolean(
        string='pedido', compute='_compute_x_studio_pedido', store=True)

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
        for record in self:
            record.x_sale_id_stock_picking_count = self.env['stock.picking'].search_count(
                [('sale_id', '=', record.id)])

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

    @api.depends('order_line', 'order_line.x_pedido', 'write_date')
    def _compute_x_studio_pedido(self):
        for record in self:
            record.x_studio_pedido = False if False in record.mapped('order_line.x_pedido') else True


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    x_comision = fields.Monetary(
        string='Comisión', compute='_compute_x_comision', store=True)
    x_invoiced_subtotal = fields.Float(
        string='Subtotal facturado', compute='_compute_x_invoiced_subtotal')
    x_por_surtir = fields.Float(
        string='Por Surtir', compute='_compute_x_por_surtir', store=True)
    x_precio_iva = fields.Float(
        string='Precio + IVA', compute='_compute_x_precio_iva', store=True)
    x_subtotal_iva = fields.Float(
        string='Subtotal + IVA', compute='_compute_x_subtotal_iva', store=True)
    x_utilidad = fields.Float(
        string='Utilidad %', compute='_compute_x_utilidad', store=True)
    # MIGRACIÓN V19: usa ubicaciones de almacén (`location_id`) fijas por id
    # (187 y 80), copiadas tal cual del cálculo original de Studio. Esos ids
    # son específicos de la base de datos de producción de origen; hay que
    # verificar que sigan siendo válidos en la base de destino antes de usar
    # este campo.
    x_studio_disponible = fields.Char(
        string='Disponible', compute='_compute_x_studio_disponible', store=True)

    @api.depends('price_unit', 'comision')
    def _compute_x_comision(self):
        for record in self:
            record.x_comision = record.price_unit * record.comision

    @api.depends('qty_invoiced', 'price_unit')
    def _compute_x_invoiced_subtotal(self):
        for record in self:
            record.x_invoiced_subtotal = record.qty_invoiced * record.price_unit

    @api.depends('product_uom_qty', 'x_Reservado', 'qty_delivered')
    def _compute_x_por_surtir(self):
        for record in self:
            if record.qty_delivered == 0:
                record.x_por_surtir = record.product_uom_qty - record.x_Reservado
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
