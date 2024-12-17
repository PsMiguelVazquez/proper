from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class AccountAccount(models.Model):
    _inherit = 'account.account'
    
    @api.onchange('name')
    def onchange_accunt_name(self):
        _logger.error('Entre onchange_accunt_name {}'.format(self.name))
        if self.name:
            cuenta = self.search([('name', '=', self.name)], limit=1)
            if cuenta:
                raise ValidationError(f"La cuenta '{self.name}' ya existe con ID: {cuenta.code}")
                
            