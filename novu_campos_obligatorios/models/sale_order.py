from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    numero_serie = fields.Char(string='No. de Serie')
    numero_motor = fields.Char(string='No. de Motor')