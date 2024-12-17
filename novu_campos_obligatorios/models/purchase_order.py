from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    def button_confirm(self):
        for order in self:
            partner = order.partner_id
            if partner.parent_id:
                empresa = partner.parent_id
                if not empresa.l10n_mx_type_of_operation:
                    raise ValidationError(f'El campo Tipo de Operacion (DIOT) en el contacto {empresa.name} es requerido')
            else:
                if not partner.l10n_mx_type_of_operation:
                    raise ValidationError(f'El campo Tipo de Operacion (DIOT) en el contacto {partner.name} es requerido')
        return super(PurchaseOrder, self).button_confirm()