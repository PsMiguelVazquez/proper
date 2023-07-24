# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class Neteo(models.Model):
    _name = 'neteo.move'
    _inherits = {'account.move': 'move_id'}
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Neteos (Pago por compensación)"
    factura_cliente = fields.Many2one('account.move', string='Factura de cliente')
    facturas_proveedor = fields.Many2many('account.move', string='Factura de proveedor')
    amount = fields.Float('Monto pagado')
    partner_id = fields.Many2one('res.partner')
    # journal_id = fields.Many2one('account.journal')




    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['move_type'] = 'entry'
            if 'currency_id' not in vals:
                journal = self.env['account.journal'].browse(vals['journal_id'])
                vals['currency_id'] = journal.currency_id.id or journal.company_id.currency_id.id
        neteo = super().create(vals_list)
        return neteo

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

    def button_open_invoices(self):
        print(self)

    def button_draft(self):
        super(Neteo, self).button_draft()


