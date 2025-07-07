# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime
import logging
_logger = logging.getLogger(__name__)
from odoo import api, fields, models
from odoo.tools.sql import column_exists, create_column


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    engine_number = fields.Char(string='Número de motor')

    def _auto_init(self):
        """ Create column for 'expiration_date' here to avoid MemoryError when letting
        the ORM compute it after module installation. Since both 'lot_id.expiration_date'
        and 'product_id.use_expiration_date' are new fields introduced in this module,
        there is no need for an UPDATE statement here.
        """
        if not column_exists(self._cr, "stock_move_line", "engine_number"):
            create_column(self._cr, "stock_move_line", "engine_number", "varchar")
        return super()._auto_init()



    def _get_value_production_lot(self):
        _logger.error("Entre Prepare new lot vals")
        vals = super()._get_value_production_lot()
        if self.engine_number:
            vals['engine_number'] = self.engine_number
        return vals
