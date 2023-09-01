# -*- coding: utf-8 -*-
from lxml import etree

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class DataValidate(models.Model):
    _name = 'data.validate'

    order_line_id = fields.Many2one('sale.order.line', string='Línea de la orden')
    product_id = fields.Many2one('product.product', string='Producto', related='order_line_id.product_id')
    branch = fields.Selection(string='Rama', related='product_id.product_tmpl_id.x_studio_rama')
    proposal_id = fields.Many2one('proposal.purchases', related='order_line_id.proposal_id', )
    order_partner_id = fields.Many2one('res.partner', string='Cliente', related='order_line_id.order_partner_id')
    order_id = fields.Many2one('sale.order', string='Referencia de la orden', related='order_line_id.order_id')
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
