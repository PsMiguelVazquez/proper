from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    captado_en = fields.Char(string="Captado en")
    mensaje = fields.Char(string="Mensaje de interes")