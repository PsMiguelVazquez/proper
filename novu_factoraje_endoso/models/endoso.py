# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class Endoso(models.Model):
    _name = 'endoso.move'
    _inherits = {'account.move': 'move_id'}
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Endosos"

    origin_invoice = fields.Many2one('account.move', string='Factura endosada')
    origin_partner_id = fields.Many2one('res.partner', string="Cliente de la factura")
    # partner_id = fields.Many2one('res.partner', string="Cliente del endoso")
    amount = fields.Monetary(currency_field='currency_id')
    amount_residual = fields.Monetary('Monto restante')
    amount_paid = fields.Monetary('Monto pagado', compute='_compute_amount_paid')
    origin_invoice_sale_id = fields.Many2one('sale.order', compute='_compute_invoice_fields', string='Venta')
    origin_invoice_date = fields.Date(compute='_compute_invoice_fields', string='Fecha de la factura')
    origin_invoice_payment_term_id = fields.Many2one('account.payment.term', compute='_compute_invoice_fields', string='Términos de pago de la factura')
    origin_invoice_warehouse_id = fields.Char(compute='_compute_invoice_fields', string='Almacén')
    origin_invoice_orden_compra = fields.Char(compute='_compute_invoice_fields', string='Orden de compra')
    origin_invoice_referencia = fields.Char(compute='_compute_invoice_fields', string='Referencia')
    origin_invoice_cfdi_uuid = fields.Char(string='Folio fiscal de la factura', related='origin_invoice.l10n_mx_edi_cfdi_uuid')
    l10n_mx_edi_cfdi_uuid = fields.Char(string='Folio fiscal',related='origin_invoice.l10n_mx_edi_cfdi_uuid')
    l10n_mx_edi_origin = fields.Char(string='CFDI de origen',related='origin_invoice.l10n_mx_edi_cfdi_uuid')
    l10n_mx_edi_cfdi_request = fields.Char(compute='compute_cfdi_request')
    # edi_document_ids = fields.One2many(comodel_name='account.edi.document', inverse_name='move_id')
    edi_document_ids = fields.One2many(comodel_name='account.edi.document', related='origin_invoice.edi_document_ids',inverse_name='move_id')
    invoice_date = fields.Date(string='Fecha de factura',related='origin_invoice.invoice_date')
    payment_state = fields.Selection(string='Estado de pago', selection=[('not_paid','not_paid'),('paid','paid'), ('partial','partial')], default='not_paid', compute='_compute_payment_state')

    def _compute_amount_paid(self):
        for record in self:
            pay_rec_lines = record.line_ids.filtered(
                lambda line: line.account_internal_type in ('receivable', 'payable')).filtered(lambda y: y.partner_id == record.partner_id)
            record.amount_paid = sum(pay_rec_lines.mapped('matched_credit_ids.amount'))
            record.move_id.amount_residual = record.amount - record.amount_paid
            record.move_id.amount_residual_signed = record.amount - record.amount_paid
    def compute_cfdi_request(self):
        for record in self:
            record.l10n_mx_edi_cfdi_request = record.origin_invoice.l10n_mx_edi_cfdi_request
            record.move_id.l10n_mx_edi_cfdi_request = record.origin_invoice.l10n_mx_edi_cfdi_request
    @api.depends('amount_paid')
    def _compute_payment_state(self):
        for record in self:
            if record.amount_paid == 0.00:
                record.payment_state = 'not_paid'
                record.move_id.payment_state = 'not_paid'
            elif record.amount - record.amount_paid > 0.00:
                record.payment_state = 'partial'
                record.move_id.payment_state = 'partial'
            elif record.amount ==  record.amount_paid:
                record.payment_state = 'paid'
                record.move_id.payment_state = 'paid'
            record.amount_residual = record.amount - record.amount_paid
            record.move_id.payment_state = record.payment_state
            # inv_ori = record.origin_invoice
            # record.move_id.write({
            #     'amount_untaxed': inv_ori.amount_untaxed,
            #     'amount_tax': inv_ori.amount_tax,
            #     'amount_total': inv_ori.amount_total,
            #     'amount_residual': inv_ori.amount_total,
            #     'amount_untaxed_signed': inv_ori.amount_untaxed_signed,
            #     'amount_tax_signed': inv_ori.amount_tax_signed,
            #     'amount_total_signed': inv_ori.amount_total_signed,
            #     'amount_residual_signed': inv_ori.amount_total,
            #     'payment_state': 'not_paid',
            #     'porcent_assign': 0.0,
            #     'es_endoso': True
            # })

    def _compute_invoice_fields(self):
        for record in self:
            record.origin_invoice_sale_id = record.origin_invoice.sale_id
            record.origin_invoice_date = record.origin_invoice.invoice_date
            record.origin_invoice_payment_term_id = record.origin_invoice.invoice_payment_term_id
            record.origin_invoice_warehouse_id = record.origin_invoice.x_studio_almacn
            record.origin_invoice_orden_compra = record.origin_invoice.x_studio_n_orden_de_compra
            record.origin_invoice_referencia = record.origin_invoice.x_referencia

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['move_type'] = 'entry'
            if 'currency_id' not in vals:
                journal = self.env['account.journal'].browse(vals['journal_id'])
                vals['currency_id'] = journal.currency_id.id or journal.company_id.currency_id.id
        endosos = super().create(vals_list)
        inv_ori = endosos.origin_invoice
        endosos.move_id.invoice_date = endosos.invoice_date
        endosos.amount_residual = endosos.amount - endosos.amount_paid
        endosos.move_id.write({
            'amount_untaxed': inv_ori.amount_untaxed,
            'amount_tax': inv_ori.amount_tax,
            'amount_total': inv_ori.amount_total,
            'amount_residual': inv_ori.amount_total,
            'amount_untaxed_signed': inv_ori.amount_untaxed_signed,
            'amount_tax_signed': inv_ori.amount_tax_signed,
            'amount_total_signed': inv_ori.amount_total_signed,
            'amount_residual_signed': inv_ori.amount_total,
            'payment_state': 'not_paid',
            'porcent_assign': 0.0,
            'es_endoso': True
        })
        return endosos

    def write(self, vals):
        # OVERRIDE
        res = super().write(vals)
        return res

    def action_post(self):
        ''' draft -> posted '''
        self.move_id._post(soft=False)

    def action_cancel(self):
        ''' draft -> cancelled '''
        self.move_id.write({'auto_post': False, 'state': 'cancel'})

    def action_draft(self):
        ''' posted -> draft '''
        self.move_id.button_draft()

    @api.depends('move_id.name')
    def name_get(self):
        return [(endoso.id, endoso.move_id.name != '/' and endoso.move_id.name or _('Borrador de endoso')) for endoso in
                self]


    def button_open_invoices(self):
        print(self)

