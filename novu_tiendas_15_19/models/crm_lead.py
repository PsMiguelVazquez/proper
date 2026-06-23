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
        readonly=True,
        selection=[('1_50', '1 - 50 Empleados'),
                    ('51_200', '51 - 200 Empleados'),
                    ('201_1000', '201 - 1000 Empleados'),
                    ('1000_plus', '+ 1000 Empleados')]
                   )

    rfc_empresa = fields.Char(
        string='RFC', 
        help="RFC")
    
    industria = fields.Char(
        string="Industria",
        readonly=True
                   )

    tipo_proyecto = fields.Char(
        string="Tipo de proyecto",
        readonly=True,
        )

    volumen_compra_estimado = fields.Char(
        string="Volumen de compra estimado",
        readonly=True,
            )
    
    fecuencia_compra_estimado = fields.Char(
        string="Frecuencia de compra estimada",
        readonly=True,
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