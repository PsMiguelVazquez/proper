# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _

# V18 -----------------------------------------------
# Se comenta por que en la V19 ya no es valido
#from odoo.osv import expression
# V18 -----------------------------------------------

class Sale(models.Model):
    _inherit = 'sale.order'
    carrier_tracking_ref = fields.Char('No de Guia')
    guia = fields.Char('No de Guia')

    def write(self, values):
        # V18 ----------------------------------------------------------------------
        # r = super(Sale, self).write(values)
        # V18 ----------------------------------------------------------------------

        # V19 ----------------------------------------------------------------------
        r = super().write(values)
        # V19 ----------------------------------------------------------------------
        if 'guia' in values:
            for pi in self.picking_ids:
                pi.write({'guia': values['guia']})
        return r