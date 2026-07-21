# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    edit_blocked = fields.Boolean('Bloqueado', default=False, compute='_compute_edit_blocked')
    # MIGRACIÓN V19: mismo fix que en `block_edit_sale_order/models/sale_order.py`
    # (ver ese archivo para el detalle): `selection_add` en vez de
    # sobreescribir la selección completa a mano.
    invoice_status = fields.Selection(
        selection_add=[('reverted', 'Nota de crédito aplicada'), ('no',)],
        ondelete={'reverted': 'set null'},
        compute='_compute_invoice_status', store=True,
    )
    credit_notes = fields.Many2many('account.move', string='Notas de crédito relacionadas', compute='get_credit_notes')
    block_invoicing = fields.Boolean(compute='_compute_block_invoicing')
    invoice_approved = fields.Boolean(default=False)
    approve_invoicing_requested = fields.Boolean(default=False)

    def request_approve_invoicing(self):
        self.approve_invoicing_requested = True
        activity_user = self.env['res.users'].search([('login', 'like', '%compras1%')])
        self.activity_schedule(
            activity_type_id=4,
            summary="Solicitud de facturacion para orden parcial",
            note='',
            user_id=activity_user.id
        )

    def approve_invoicing(self):
        self.invoice_approved = not self.invoice_approved
        self.approve_invoicing_requested = False
        self.activity_schedule(
            activity_type_id=4,
            summary="La solicitud de facturación ha sido aceptada",
            note='',
            user_id=self.user_id.id
        )

    def reject_invoicing(self):
        self.approve_invoicing_requested = False
        self.activity_schedule(
            activity_type_id=4,
            summary="La solicitud de facturación ha sido rechazada",
            note='',
            user_id=self.user_id.id
        )

    @api.depends('state')
    def _compute_block_invoicing(self):
        for record in self:
            record.block_invoicing = record.invoice_status != 'to_invoice' and record.es_orden_parcial and not record.invoice_approved

    @api.depends('state')
    def _compute_edit_blocked(self):
        for record in self:
            record.edit_blocked = record.state not in ['draft', 'sent']

    @api.depends('invoice_ids')
    def get_credit_notes(self):
        for record in self:
            record.credit_notes = record.invoice_ids.filtered(lambda x: x.move_type == 'out_refund')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    cantidad_por_comprar = fields.Float('Cantidad pendiente de compra', compute='_compute_cantidad_por_comprar')
    cantidad_vendida_kits = fields.Float('Cantidad vendida en kits', compute='_compute_cantidad_vendida_kits')
    description = fields.Char('Descripción')
    # MIGRACIÓN V19: `x_obse_comprador` (Studio, "Línea de la orden de venta")
    # es un campo de texto usado por `data.validate`; se formaliza aquí.
    x_obse_comprador = fields.Text(string='Observaciones comprador')

    def _compute_cantidad_por_comprar(self):
        for record in self:
            if record.order_id.es_orden_parcial:
                record.cantidad_por_comprar = record.product_uom_qty - record.cantidad_asignada - record.qty_delivered
            else:
                record.cantidad_por_comprar = 0.0

    def _compute_cantidad_vendida_kits(self):
        for record in self:
            record.cantidad_vendida_kits = 0
            kits = record.product_id.bom_line_ids.mapped('bom_id')
            for kit in kits:
                lines = self.env['sale.order.line'].search([
                    ('product_id', '=', kit.product_tmpl_id.product_variant_id.id),
                    ('order_id.state', '=', 'sale')])
                record.cantidad_vendida_kits += (sum(lines.mapped('product_uom_qty')) *
                                                  sum(kit.bom_line_ids.filtered(lambda y: y.product_id == record.product_id).mapped('product_qty')))


# MIGRACIÓN V19: `x_studio_rama` (Studio, "Plantilla de producto") se había
# declarado aquí como "mejor esfuerzo" (sin el listado real confirmado en
# ese momento, reutilizando el conjunto de `wizard.proposal.x_rama`). Ya se
# formalizó con el listado completo y confirmado (12 valores, del export
# real de Studio) en `studio_fields_v19/models/product_template.py`; tener
# el campo declarado en dos módulos sin relación de dependencia entre sí
# hace que el orden de carga (no garantizado) decida cuál selección "gana"
# -de ahí el warning "overrides existing selection"-, así que se quita esta
# versión incompleta.
