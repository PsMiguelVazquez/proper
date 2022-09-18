# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
from .. import extensions
from odoo.exceptions import UserError


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    origin = fields.Char(related='move_id.origin', string='Source', store=True)

    def solict_reserved(self):
        if self.origin:
            sale = self.env['sale.order'].search([['name', '=', self.origin]])
            user = self.env.user
            message = "El usuario "+str(user.name)+"\n"+"Requiere el producto "+str(self.product_id.name)
            sale.message_post(body=message, partner_ids=sale.user_id.ids)