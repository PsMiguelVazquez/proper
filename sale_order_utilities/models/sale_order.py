# -*- coding: utf-8 -*-
from lxml import etree

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    edit_blocked = fields.Boolean('Bloqueado', default=False, compute='_compute_edit_blocked')
    invoice_status = fields.Selection([
        ('upselling', 'Upselling Opportunity'),
        ('invoiced', 'Fully Invoiced'),
        ('to invoice', 'To Invoice'),
        ('reverted', 'Nota de crédito aplicada'),
        ('no', 'Nothing to Invoice')
    ], string='Invoice Status', compute='_get_invoice_status', store=True)
    credit_notes = fields.Many2many('account.move', string='Notas de crédito relacionadas', compute='get_credit_notes')
    block_invoicing = fields.Boolean(compute='_compute_block_invoicing')
    invoice_approved = fields.Boolean(default=False)
    approve_invoicing_requested = fields.Boolean(default=False)

    def show_confirm_sale_wizard(self):
        lines = self.order_line.filtered(lambda x: (
                        x.product_id.stock_quant_warehouse_zero + x.x_cantidad_disponible_compra - x.product_uom_qty) < 0
                        and x.x_validacion_precio == True)
        w = self.env['sale.purchase.order.alerta'].create({'res_order_id': self.id ,'message_top': '<h3>TOP</h3>', 'lines':lines, 'message_bottom': '<h3>BOTTOM</h3>'})
        view = self.env.ref('sale_order_utilities.sale_purchase_order_alerta')
        return {
            'name': _('Confirmar solicitud de compra'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.purchase.order.alerta',
            'view_mode': 'form',
            'res_id': w.id,
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new'
        }

    def request_approve_invoicing(self):
        self.approve_invoicing_requested = True

    def approve_invoicing(self):
        self.invoice_approved = not self.invoice_approved
        self.approve_invoicing_requested = False

    @api.depends('state')
    def _compute_block_invoicing(self):
        for record in self:
            record.block_invoicing = record.invoice_status != 'to_invoice' and record.es_orden_parcial and not record.invoice_approved

    @api.depends('state')
    def _compute_edit_blocked(self):
        for record in self:
            record.edit_blocked = record.state not in ['draft']
            # record.edit_blocked = False

    @api.depends('invoice_ids')
    def get_credit_notes(self):
        for record in self:
            record.credit_notes = record.invoice_ids.filtered(lambda x: x.move_type == 'out_refund')

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    atendido_por = fields.Many2one('res.users', compute='_on_change_x_solicitud_atendida', store=True)
    compra_confirmada = fields.Boolean(default=False)
    cantidad_a_comprar = fields.Integer(string='Cantidad a comprar')
    proveedor_propuesta = fields.Char()


    @api.depends('x_solicitud_atendida')
    def _on_change_x_solicitud_atendida(self):
        for record in self:
            if record.x_solicitud_atendida == 'Atendido':
                record.atendido_por = self.env.uid
            else:
                record.atendido_por = None




