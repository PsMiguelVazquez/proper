# -*- coding: utf-8 -*-
from lxml import etree

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    edit_blocked = fields.Boolean('Bloqueado', default=False, compute='_compute_edit_blocked')
    # MIGRACIÓN V19: el compute del core se renombró de `_get_invoice_status`
    # a `_compute_invoice_status`; hay que apuntar al nombre actual. Antes se
    # sobreescribía la selección completa a mano (mismo problema que
    # `purchase.order.state`: "overrides existing selection"); se usa
    # `selection_add` para sólo agregar 'reverted' sobre la selección real
    # del core. `ondelete='set null'` (no 'cascade', que borraría la orden
    # completa; ni 'set default', inválido aquí porque el campo no tiene un
    # `default=` propio al ser 100% compute) para que, si este módulo se
    # desinstala, la orden sólo pierda ese valor -se recalcula solo en la
    # próxima recomputación- en vez de borrarse.
    invoice_status = fields.Selection(
        selection_add=[('reverted', 'Nota de crédito aplicada'), ('no',)],
        ondelete={'reverted': 'set null'},
        compute='_compute_invoice_status', store=True,
    )
    credit_notes = fields.Many2many('account.move', string='Notas de crédito relacionadas', compute='get_credit_notes')
    block_invoicing = fields.Boolean(compute='_compute_block_invoicing')
    invoice_approved = fields.Boolean(compute='_compute_invoice_approved', store=True)
    approve_invoicing_requested = fields.Boolean(default=False)

    def request_approve_invoicing(self):
        self.approve_invoicing_requested = True

    def _compute_invoice_approved(self):
        for record in self:
            record.invoice_approved = True

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

    @api.depends('invoice_ids')
    def get_credit_notes(self):
        for record in self:
            record.credit_notes = record.invoice_ids.filtered(lambda x: x.move_type == 'out_refund')
