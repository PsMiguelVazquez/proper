# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    productos_entregados = fields.Integer('Productos entregados', compute='compute_productos_entregados')

    def compute_productos_entregados(self):
        for record in self:
            record.productos_entregados = sum(record.move_ids_without_package.mapped('quantity_done'))