# -*- coding: utf-8 -*-
import odoo.exceptions
from odoo import models, fields, api,_
from .. import extensions


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    total_in_text = fields.Char(compute='set_amount_text', string='Total en letra')
    sale_ids = fields.Many2many('sale.order', string="SO")
    active = fields.Boolean(default=True)

    @api.depends('amount_total')
    def set_amount_text(self):
        for record in self:
            if record.amount_total:
                record.total_in_text = extensions.text_converter.number_to_text_es(record.amount_total)
            else:
                record.total_in_text = extensions.text_converter.number_to_text_es(0)

    def action_mass_confirm(self):
        purchases = self
        return purchases.button_confirm()


class PurchaseWizard(models.TransientModel):
    _name = 'purchase.wizard.conf'

    def confirm(self):
        purchases = self.env['purchase.order'].browse(self._context.get('active_ids', []))
        return purchases.action_mass_confirm()


class PurchaseWizardMerge(models.TransientModel):
    _name = 'purchase.wizard.merge'

    def confirm(self):
        purchases = self.env['purchase.order'].browse(self._context.get('active_ids', [])).filtered(lambda x: x.state == 'draft')
        partners = purchases.mapped('partner_id')
        for pa in partners:
            pl = purchases.filtered(lambda x: x.partner_id.id == pa.id)
            pl_lines = pl.mapped('order_line')
            orden = self.env['purchase.order'].create({'partner_id': pa.id})
            pl_lines.write({'order_id': orden.id})
            pl.write({'active':False})
        return {
            'name':_("Ordens"),
            'view_mode': 'tree',
            'view_id': False,
            'view_type': 'tree',
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
        }