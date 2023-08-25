# -*- coding: utf-8 -*-
from lxml import etree

from odoo import models, fields, api
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
    allow_invoicing = fields.Boolean(string='Permitir facturar', compute='_compute_allow_invoicing')
    invoice_allowed = fields.Boolean(string='Facturación de orden parcial permitida', default=False)

    @api.depends('state')
    def _compute_allow_invoicing(self):
        for record in self:
            op = False
            if record.order_line.filtered(
                    lambda x: x.cantidad_asignada + x.qty_delivered + x.qty_invoiced < x.product_uom_qty) and record.state == 'sale':
                op = True
            record.allow_invoicing = 1
            print(record.allow_invoicing)

    @api.depends('state')
    def _compute_edit_blocked(self):
        for record in self:
            # record.edit_blocked = record.state not in ['draft']
            record.edit_blocked = False

    @api.depends('invoice_ids')
    def get_credit_notes(self):
        for record in self:
            record.credit_notes = record.invoice_ids.filtered(lambda x: x.move_type == 'out_refund')
            # if record.invoice_status == 'to invoice':
            #     if 'reversed' in record.invoice_ids.mapped('payment_state'):
            #         record.invoice_status = 'reverted'




