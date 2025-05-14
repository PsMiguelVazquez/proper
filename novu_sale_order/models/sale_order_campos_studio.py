from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'


    #CAMPOS QUE SE CREARON DESDE STUDIO


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    x_Reservado = fields.Float(string="Reservado", readonly=True, store=True, related="order_id.picking_ids.move_line_ids.quantity")
    