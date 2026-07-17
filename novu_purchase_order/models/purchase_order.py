from odoo import models, fields
import io
import logging
_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    x_studio_many2one_field_UTgPw = fields.Many2one('sale.order', string="Pedido de Venta")