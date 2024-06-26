from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    #ine = fields.Boolean(string='INE', default=False)
    #identificacion_representante_legal = fields.Boolean(string='Identificación de representante legal', default=False)
    #llenado_solicitud = fields.Boolean(string='Llenado de solicitud', default=False)

    giro_segmento = fields.Char(string='GIRO-SEGMENTO')
    temporalidad = fields.Char(string='Temporalidad')


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            #if not vals.get('partner_name'):
                #raise ValidationError('El campo Nombre empresa es requerido.')
            _logger.error('vals {}'.format(vals))
            if vals.get('contact_name') == None or vals.get('contact_name') =='' :
                _logger.error('contact_name {}'.format(vals.get('contact_name')))
                raise ValidationError('El campo Nombre del contacto es requerido.')
            if not vals.get('email_from'):
                raise ValidationError('El campo Correo Electronico es requerido.')
            if not vals.get('phone'):
                raise ValidationError('El campo Telefono es requerido.')
                
        leads = super(CrmLead, self).create(vals_list)

        return leads 


    def write(self, vals):
        #if not vals.get('partner_name'):
            #raise ValidationError('El campo Nombre empresa es requerido.')
        if not vals.get('contact_name'):
            raise ValidationError('El campo Nombre de contacto es requerido.')
        if not vals.get('email_from'):
            raise ValidationError('El campo Correo es requerido.')
        if not vals.get('phone'):
            raise ValidationError('El campo Telefono es requerido.')
        
        result = super(Lead, leads_already_won).write(vals)
        return result