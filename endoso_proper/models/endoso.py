# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class Endoso(models.Model):
    _name = 'endoso.move'
    _inherits = {'account.move': 'move_id'}
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Endosos"
    _order = "date desc, name desc"
    name = fields.Char()
    outstanding_account_id = fields.Many2one(
        comodel_name='account.account',
        string="Outstanding Account",
        check_company=True)
    destination_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Destination Account',
        store=True,
        check_company=True)
    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Destination Journal',
        check_company=True,
    )
    origin_invoice = fields.Many2one('account.move', string='Factura endosada')
    origin_partner_id = fields.Many2one('res.partner', string="Cliente de la factura")
    partner_id = fields.Many2one('res.partner', string="Cliente del endoso")
    move_id = fields.Many2one(
        comodel_name='account.move',
        string='Journal Entry', required=True, readonly=True, ondelete='cascade',
        check_company=True)
    amount = fields.Monetary(currency_field='currency_id')

    # sale_id = fields.Many2one('sale_order', related='origin_invoice.sale_id')
    # cfdi_uuid = fields.Char(related='origin_invoice.l10n_mx_edi_cfdi_uuid')
    # invoice_date = fields.Date(related='origin_invoice.invoice_date')
    # invoice_payment_term_id = fields.Many2one('account.payment.term', related='origin_invoice.invoice_payment_term_id')
    # warehouse_id = fields.Char(related='origin_invoice.x_studio_almacn')
    # orden_compra = fields.Char(related='origin_invoice.x_studio_n_orden_de_compra')
    # referencia = fields.Char(related='origin_invoice.x_referencia')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['move_type'] = 'entry'
            if 'journal_id' not in vals:
                vals['journal_id'] = self.move_id._get_default_journal().id

            if 'currency_id' not in vals:
                journal = self.env['account.journal'].browse(vals['journal_id'])
                vals['currency_id'] = journal.currency_id.id or journal.company_id.currency_id.id
        endosos = super().create(vals_list)
        endosos.move_id.name = endosos.name
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
        return [(endoso.id, endoso.move_id.name != '/' and endoso.move_id.name or _('Draft Payment')) for endoso in
                self]


