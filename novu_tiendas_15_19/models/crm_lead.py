from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    captado_en = fields.Char(string="Captado en")
    mensaje = fields.Char(string="Mensaje de interes")
    tamanio_empresa = fields.Selection(
        string="Tamaño de la empresa",
        selection=[('1_50', '1 - 50 Empleados'),
                    ('51_200', '51 - 200 Empleados'),
                    ('201_1000', '201 - 1000 Empleados'),
                    ('1000_plus', '+ 1000 Empleados')]
                   )

    @api.model
    def create(self, vals):
        if vals.get('captado_en') == 'PROPER V19':
            vendedor = self.env['res.users'].search([
                ('login', '=', 'mercadotecnia-ps@properservices.com.mx')
            ], limit=1)

            if vendedor:
                vals['user_id'] = vendedor.id

            if vals.get('mensaje'):
                msj = vals.get('mensaje')
                vals['description'] = msj

        return super(CrmLead, self).create(vals)