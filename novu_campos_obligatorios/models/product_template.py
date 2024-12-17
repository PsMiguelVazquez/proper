from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    tracking = fields.Selection(
        selection_add=[
            ('serialandmotornumber', 'Por numero de serie y numero de motor unicos')  # Nueva opción añadida
        ],
        ondelete={'serialandmotornumber': 'set default'}) 
    
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not 'unspsc_code_id' in vals:
                raise ValidationError("El campo Clave SAT en el producto es requerido.")
            #if not 'weight' in vals:
                #raise ValidationError("El campo Peso en el producto es requerido.")
                

        return super(ProductTemplate, self).create(vals_list)


    def write(self, vals):
        #Si no viene en la edicion y no esta seteado ya manda el error
        if not 'unspsc_code_id' in vals and not self.unspsc_code_id:
            raise ValidationError("El campo Clave SAT en el producto es requerido.")

        #Si viene la Clave SAT en los valores a editar pero le quitaron el dato manda el error.
        if 'unspsc_code_id' in vals and vals['unspsc_code_id'] is False:
            raise ValidationError("El campo Clave SAT en el producto es requerido.")
        
        #if not 'weight' in vals and not self.weight:
            #raise ValidationError("El campo Peso en el producto es requerido.")

        #if 'weight' in vals and (vals['weight'] is False or vals['weight'] == 0.0):
            #raise ValidationError("El campo Peso en el producto es requerido.")

        return super(ProductTemplate, self).write(vals)