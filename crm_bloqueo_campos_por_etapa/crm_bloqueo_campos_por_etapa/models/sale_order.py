from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # V18 --------------------------------------------------------------------------------------------------------------------------------------
    def action_confirm(self):
        res = super(SaleOrder, self.with_context({k: v for k, v in self._context.items() if k != 'default_tag_ids'})).action_confirm()
        for order in self:
            # Evitamos validación de etapa "Ganado" cuando viene de venta
            order.opportunity_id.with_context(skip_ganado_check=True)._update_revenues_from_so(order)
        return res
    # V18 --------------------------------------------------------------------------------------------------------------------------------------

    # V19 --------------------------------------------------------------------------------------------------------------------------------------
    # def action_confirm(self):
    #     ctx = dict(self.env.context)
    #     ctx.pop('default_tag_ids', None)
    
    #     res = super().with_context(ctx).action_confirm()
    
    #     for order in self:
    #         if order.opportunity_id:
    #             order.opportunity_id.with_context(
    #                 skip_ganado_check=True
    #             )._update_revenues_from_so(order)
    
    #     return res
    # V19 --------------------------------------------------------------------------------------------------------------------------------------