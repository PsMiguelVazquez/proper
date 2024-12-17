from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    numero_motor = fields.Char('Motor Number Name')
    tracking = fields.Selection(realted="product_id.tracking", compute="_compute_product_tracking")

    def _compute_product_tracking(self):
        for record in self:
            # Busca el producto basado en el campo `product_id` y obtiene su configuración de seguimiento
            product = self.env['product.template'].search([('id', '=', record.product_id.id)], limit=1)
            record.tracking = product.tracking if product else ''
    