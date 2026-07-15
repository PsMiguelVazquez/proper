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


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    sale = fields.Many2one('sale.order')
    # MIGRACIÓN V19: `x_studio_facturas` (Studio, "Traslado") es un Many2many
    # a account.move relacionado con `sale_id.invoice_ids`, usado por
    # `account_move_proper`. `sale_id` era en sí otro campo de Studio
    # (duplicado de este mismo `sale`, ver `x_studio_many2one_field_uXDXF`
    # en el export); se enlaza directamente al `sale` ya formalizado aquí.
    x_studio_facturas = fields.Many2many('account.move', string='Facturas', related='sale.invoice_ids')


class StockMove(models.Model):
    _inherit = 'stock.move'

    # MIGRACIÓN V19: `_action_confirm()` del core ahora acepta también
    # `create_proc`; sin declararlo aquí, cualquier llamada interna del core
    # que lo pase (p. ej. `_create_backorder()`) fallaba con
    # "unexpected keyword argument 'create_proc'". Se agrega y se reenvía.
    def _action_confirm(self, merge=True, merge_into=False, create_proc=True):
        return super(StockMove, self)._action_confirm(merge=False, merge_into=merge_into, create_proc=create_proc)


class productPr(models.Model):
    _inherit = 'product.product'
    move_in = fields.Float(compute='_get_in_out')

    # MIGRACIÓN V19: `x_studio_ultimo_costo` ahora se calcula en
    # `product.py` con la fórmula real de Studio (basada en
    # `stock.valuation.layer`), así que ya no se escribe aquí como efecto
    # secundario de este compute -ambas cosas escribiendo el mismo campo
    # entraban en conflicto-.
    @api.depends('qty_available')
    def _get_in_out(self):
        for record in self:
            location_supplier = self.env.ref('stock.stock_location_suppliers').id
            picking_in = False
            if record.id:
                move_in = self.env['stock.move.line'].search([['product_id', '=', record.id], ['location_id', '=', location_supplier]], order='id desc', limit=1)
                if move_in.id:
                    picking_in = move_in.move_id.mapped('purchase_line_id.price_unit')[-1]
            record.move_in = picking_in
