# -*- coding: utf-8 -*-pack
from odoo import models, fields, api, _

from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class ProductProduct(models.Model):
    _inherit = "product.product"
    # x_studio_related_field_HW6gD = fields.Selection()