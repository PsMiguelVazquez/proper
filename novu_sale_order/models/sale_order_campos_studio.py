from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'


    #CAMPOS QUE SE CREARON DESDE STUDIO

    def _confirmation_error_message(self):
        """ Return whether order can be confirmed or not if not then returm error message. """
        self.ensure_one()
        if self.state not in {'draft', 'sent', 'sale_conf', 'purchase_conf', 'credito_conf'}:
            return _("Some orders are not in a state requiring confirmation.")
        if any(
            not line.display_type
            and not line.is_downpayment
            and not line.product_id
            for line in self.order_line
        ):
            return _("A line on these orders missing a product, you cannot confirm it.")

        return False

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    x_Reservado = fields.Float(string="Reservado", readonly=True, store=True, related="order_id.picking_ids.move_line_ids.quantity")

    