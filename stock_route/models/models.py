# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockRoute(models.Model):
    _name = 'stock.route'


class StockPicking(models.Model):
    _name = 'stock.picking'
