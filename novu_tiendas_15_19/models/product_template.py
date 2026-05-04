from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    de_hogar = fields.Boolean(string="De Hogar")
    proper = fields.Boolean(string="Proper")
    tienda_linea = fields.Boolean(string="Tienda en Linea")