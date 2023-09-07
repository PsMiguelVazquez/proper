# -*- coding: utf-8 -*-
from odoo import models, fields, api


class DataValidate(models.Model):
    _name = 'data.validate'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'data.validate'
    order_line_id = fields.Many2one('sale.order.line', string='Línea de la orden')
    product_id = fields.Many2one('product.product', string='Producto', related='order_line_id.product_id')
    branch = fields.Selection(string='Rama', related='product_id.product_tmpl_id.x_studio_rama')
    proposal_id = fields.Many2one('proposal.purchases', related='order_line_id.proposal_id', )
    order_partner_id = fields.Many2one('res.partner', string='Cliente', related='order_line_id.order_partner_id', store=True)
    order_id = fields.Many2one('sale.order', string='Referencia de la orden', related='order_line_id.order_id', store=True)
    salesman_id = fields.Many2one('res.users', string='Vendedor', related='order_line_id.salesman_id')
    product_uom_qty = fields.Float(string='Cantidad', related='order_line_id.product_uom_qty')
    standard_price = fields.Float(string='Costo promedio', related='order_line_id.x_studio_costo_promedio')
    requested_by = fields.Many2one('res.users', string='Atendido por')
    product_qty_purchases = fields.Float(string='Cantidad disponible')
    delivery_time = fields.Char(string='Tiempo de entrega')
    new_cost = fields.Float(string='Nuevo costo')
    note = fields.Char(string='Observaciones')
    description = fields.Char(string='Descripción')
    request_answered = fields.Selection(string='Propuesta atendida', selection=[('Atendido', 'Atendido'), ('Noatendido', 'No atendido')])


    def migrate_lines(self):
        lines_to_migrate = self.env['sale.order.line'].search([
            ('x_validacion_precio', '=' , True )
        ],order="id asc")
        for line in lines_to_migrate:
            data_validate = self.env['data.validate'].search([('order_line_id','=',line.id)])
            if not data_validate:
                self.env['data.validate'].create({
                    'order_line_id' : line.id,
                    'product_qty_purchases' : line.x_cantidad_disponible_compra,
                    'new_cost' : line.x_studio_nuevo_costo,
                    'delivery_time' : line.x_tiempo_entrega_compra,
                    'note' : line.x_obse_comprador,
                    'request_answered' : line.x_solicitud_atendida,
                })


    @api.onchange('new_cost')
    def on_change_new_cost(self):
        for record in self:
            record.order_line_id.write({
                'x_studio_nuevo_costo': record.new_cost
            })
    @api.onchange('product_qty_purchases')
    def on_change_product_qty_purchases(self):
        for record in self:
            record.order_line_id.write({
                'x_cantidad_disponible_compra': record.product_qty_purchases
            })
    @api.onchange('delivery_time')
    def on_change_delivery_time(self):
        for record in self:
            record.order_line_id.write({
                'x_tiempo_entrega_compra': record.delivery_time
            })
    @api.onchange('note')
    def on_change_note(self):
        for record in self:
            record.order_line_id.write({
                'x_obse_comprador': record.note
            })
    @api.onchange('request_answered')
    def on_change_request_answered(self):
        for record in self:
            record.order_line_id.write({
                'x_solicitud_atendida': record.request_answered
            })
            record.requested_by = self.write_uid
