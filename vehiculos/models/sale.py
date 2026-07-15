# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class Sale(models.Model):
    _inherit = 'sale.order'
    carrier_tracking_ref = fields.Char('No de Guia (Transportista)')
    guia = fields.Char('No de Guia')

    def write(self, values):
        r = super(Sale, self).write(values)
        if 'guia' in values:
            for pi in self.picking_ids:
                pi.write({'guia': values['guia']})
        return r
