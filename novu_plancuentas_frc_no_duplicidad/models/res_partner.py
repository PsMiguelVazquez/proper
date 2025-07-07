from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    @api.onchange('vat')
    def onchange_vat(self):
        _logger.error('Entre onchange_vat {}'.format(self.vat))
        if self.vat:
            vat = self.search([('vat', '=', self.vat)], limit=1)
            if vat:
                raise ValidationError(f"El RFC '{self.vat}' ya existe en el contacto: {vat.name}")