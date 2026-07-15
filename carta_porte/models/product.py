from odoo import fields, models, api, _, modules
import base64
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from odoo.exceptions import UserError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # MIGRACIÓN V19: `_sql_constraints` (lista de tuplas) fue reemplazado
    # por atributos de clase `models.Constraint()`.
    _default_code_unique = models.Constraint(
        'unique(default_code)',
        'Ya existe un producto con la misma referencia',
    )
