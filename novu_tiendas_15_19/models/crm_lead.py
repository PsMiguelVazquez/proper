from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    captado_en = fields.Char(string="Captado en")
    mensaje = fields.Char(string="Mensaje de interes")

    @api.model
    def create(self, vals):
        if vals.get('captado_en') == 'PROPER V19':
            vendedor = self.env['res.users'].search([
                ('login', '=', 'mercadotecnia-ps@properservices.com.mx')
            ], limit=1)

            if vendedor:
                vals['user_id'] = vendedor.id

        return super(CrmLead, self).create(vals)