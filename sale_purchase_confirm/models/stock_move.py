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
            sale = self.env['sale.order'].sudo().search([['name', '=', self.origin]])
            user = self.env.user
            message = "El usuario "+str(user.name)+"\n"+"Requiere el producto "+str(self.product_id.name)
            data = {
                'res_id': sale.id,
                'res_model_id': self.env['ir.model'].search([('model', '=', 'sale.order')]).id,
                'user_id': sale.sudo().user_id.id,
                'summary': message,
                'activity_type_id': self.env.ref('mail.mail_activity_data_meeting').id,
                'date_deadline': fields.Date.today()
            }
            self.env['mail.activity'].sudo().create(data)
            #sale.message_post(body=message, partner_ids=sale.user_id.partner_id.ids)


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    sale = fields.Many2one('sale.order')

class StockMove(models.Model):
    _inherit = 'stock.move'

    def _action_confirm(self, merge=True, merge_into=False):
        return super(StockMove, self)._action_confirm(merge=False, merge_into=merge_into)
