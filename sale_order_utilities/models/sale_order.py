# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    edit_blocked = fields.Boolean('Bloqueado', default=False, compute='_compute_edit_blocked')
    # MIGRACIÓN V19: el compute del core se renombró de `_get_invoice_status`
    # a `_compute_invoice_status` (mismo fix que en `block_edit_sale_order`).
    invoice_status = fields.Selection([
        ('upselling', 'Upselling Opportunity'),
        ('invoiced', 'Fully Invoiced'),
        ('to invoice', 'To Invoice'),
        ('reverted', 'Nota de crédito aplicada'),
        ('no', 'Nothing to Invoice')
    ], string='Invoice Status', compute='_compute_invoice_status', store=True)
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


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    # MIGRACIÓN V19: `x_studio_rama` (Studio, "Plantilla de producto") es un
    # campo Selección usado por `data.validate.branch`. Sin valores de
    # opción confirmados por el usuario para este campo específico, pero se
    # reutiliza el mismo conjunto que `wizard.proposal.x_rama`
    # (`sale_purchase_confirm`), claramente el mismo concepto de negocio.
    x_studio_rama = fields.Selection([
        ("SOBREPEDIDO", "SOBREPEDIDO"),
        ("LINEA", "LINEA"),
        ("OBSOLETO", "OBSOLETO"),
        ("DESCONTINUADO", "DESCONTINUADO"),
        ("CATALOGO", "CATALOGO"),
        ("ACTIVO FIJO", "ACTIVO FIJO"),
        ("ADMON", "ADMON"),
        ("PROMOCION", "PROMOCION"),
    ], string='Rama')
