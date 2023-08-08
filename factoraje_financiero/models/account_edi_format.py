
from odoo import fields,models


class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'



    def _l10n_mx_edi_export_payment_cfdi(self, move):
        r = super(AccountEdiFormat, self)._l10n_mx_edi_export_payment_cfdi(move)
        '''
            Insertar los nodos del pago por compensación aquí
        '''
        return r
