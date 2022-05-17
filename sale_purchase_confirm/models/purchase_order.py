# -*- coding: utf-8 -*-
from odoo import models, fields, api
from .. import extensions


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    #def action_confirm(self):
    #    return super(PurchaseOrder).button_confirm()

