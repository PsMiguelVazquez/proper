# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.osv import expression

class Sale(models.Model):
    _inherit = 'sale.order'
    carrier_tracking_ref = fields.Char('No de Guia')

    def write(self, values):
        if 'carrier_tracking_ref' in values and not self.picking_ids.mapped('carrier_tracking_ref'):
            self.picking_ids.write({'carrier_tracking_ref': values['carrier_tracking_ref']})
        return super(Sale, self).write(values)