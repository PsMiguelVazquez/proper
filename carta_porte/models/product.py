from odoo import fields,models, api, _, modules
import base64
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from odoo.exceptions import UserError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    _sql_constraints = [('default_code_unique', 'unique(default_code)', 'Ya existe un producto con la misma referencia')]