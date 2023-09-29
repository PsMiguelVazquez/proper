# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_round
from odoo.osv import expression

from collections import defaultdict


class MrpUnbuild(models.Model):
     _inherit = "mrp.unbuild"


     def action_validate(self):
         self.ensure_one()
         precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
         available_qty = self.env['stock.quant']._get_available_quantity(self.product_id, self.location_id, self.lot_id,
                                                                         strict=True)
         unbuild_qty = self.product_uom_id._compute_quantity(self.product_qty, self.product_id.uom_id)
         if float_compare(available_qty, unbuild_qty, precision_digits=precision) >= 0:
             return super(MrpUnbuild, self).action_validate()
         else:
             raise UserError('No puede desmantelar esta cantidad de kits porqué '
                             'no hay cantidad disponible suficiente  en el almacén.'
                             'Se pueden desmantelar ' + str(available_qty) + ' kits.')