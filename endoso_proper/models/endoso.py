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
    origin_invoice_sale_id = fields.Many2one('sale.order', compute='_compute_invoice_fields', string='Venta')
    origin_invoice_date = fields.Date(compute='_compute_invoice_fields', string='Fecha de la factura')
    origin_invoice_payment_term_id = fields.Many2one('account.payment.term', compute='_compute_invoice_fields', string='Términos de pago de la factura')
    origin_invoice_warehouse_id = fields.Char(compute='_compute_invoice_fields', string='Almacén')
    origin_invoice_orden_compra = fields.Char(compute='_compute_invoice_fields', string='Orden de compra')
    origin_invoice_referencia = fields.Char(compute='_compute_invoice_fields', string='Referencia')
    origin_invoice_cfdi_uuid = fields.Char(string='Folio fiscal de la factura', related='origin_invoice.l10n_mx_edi_cfdi_uuid')

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
        return endosos

    def write(self, vals):
        # OVERRIDE
        res = super().write(vals)
        return res

    def action_post(self):
        ''' draft -> posted '''
        self.move_id._post(soft=False)
        print(self)

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

