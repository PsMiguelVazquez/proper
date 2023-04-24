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
            message = "El usuario "+str(user.name)+"\n"+"Requiere el producto "+str(self.product_id.name)+"<br/><a class=btn-primary href=/unreserved/"+str(self.id)+"/"+str(sale.id)+" >Aceptar</a>"
            data = {
                'res_id': sale.id,
                'res_model_id': self.env['ir.model'].sudo().search([('model', '=', 'sale.order')]).id,
                'user_id': sale.sudo().user_id.id,
                'note': message,
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


class productPr(models.Model):
    _inherit = 'product.product'
    move_in = fields.Float(compute='_get_in_out')

    @api.depends('qty_available')
    def _get_in_out(self):
        for record in self:
            location_supplier = self.env.ref('stock.stock_location_suppliers').id
            picking_in = False
            if record.id:
                move_in = self.env['stock.move.line'].search([['product_id', '=', record.id], ['location_id', '=', location_supplier]], order='id desc', limit=1)
                if move_in.id:
                    picking_in = move_in.move_id.mapped('purchase_line_id.price_unit')[-1]
                    if picking_in!=0:
                        record.update({'x_studio_ultimo_costo': picking_in})
            record.move_in = picking_in
