from odoo import api,models, fields


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    @api.onchange('sale_order_id')
    def _get_default_partner_id(self):

        if self.sale_order_id:
            self.partner_id = self.sale_order_id.partner_id