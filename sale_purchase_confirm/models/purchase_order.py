# -*- coding: utf-8 -*-
from odoo import models, fields, api
from .. import extensions


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    total_in_text = fields.Char(compute='set_amount_text', string='Total en letra')

    @api.depends('amount_total')
    def set_amount_text(self):
        for record in self:
            if record.amount_total:
                record.total_in_text = extensions.text_converter.number_to_text_es(record.amount_total)
            else:
                record.total_in_text = extensions.text_converter.number_to_text_es(0)

