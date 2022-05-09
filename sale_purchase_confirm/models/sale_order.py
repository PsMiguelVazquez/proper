# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def conf_credito(self):
        self.write({'x_aprovacion_compras': True, 'x_bloque': False})
        self.action_confirm()



