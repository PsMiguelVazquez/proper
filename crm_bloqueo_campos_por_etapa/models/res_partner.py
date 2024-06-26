from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    ine = fields.Boolean(string='INE', default=False)
    identificacion_representante_legal = fields.Boolean(string='Identificación de representante legal', default=False)
    llenado_solicitud = fields.Boolean(string='Llenado de solicitud', default=False)