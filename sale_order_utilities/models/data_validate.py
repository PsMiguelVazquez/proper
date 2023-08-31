# -*- coding: utf-8 -*-
from lxml import etree

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class DataValidate(models.Model):
    _name = 'data.validate'

    product_id = fields.Many2one('product.product', string='Producto')
    proposal_id = fields.Many2one('proposal.purchases', string='Propuesta de origen')
    order_partner_id = fields.Many2one('res.partner', string='Cliente')
    order_id = fields.Many2one('sale.order', string='Referencia de la orden')
    salesman_id = fields.Many2one('res.users', string='Vendedor')
    product_uom_qty = fields.Float(string='Cantidad')
    standard_price = fields.Float(string='Costo promedio')
    product_qty_purchases = fields.Float(string='Cantidad disponible')
    delivery_time = fields.Char(string='Tiempo de entrega')
    new_cost = fields.Float(string='Nuevo costo')
    note = fields.Char(string='Observaciones')
    description = fields.Char(string='Descripción')
    branch = fields.Selection(string='Rama', related='product_id.product_tmpl_id.x_studio_rama')
    request_answered = fields.Selection(string='Propuesta atendida', selection=[('Atendido', 'Atendido'), ('Noatendido', 'No atendido')])
