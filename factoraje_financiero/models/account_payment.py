
from odoo import models

class AccountMove(models.Model):
    _inherit = 'account.payment'


    def action_draft(self):
        ''' posted -> draft '''
        self.move_id.button_draft()
        '''
            Al reestablecer a borrador un pago busca si tiene pagos por compensación y los cancela
        '''
        neteo = self.env['account.move'].search([('rel_payment','=',self.id)])
        if neteo:
            neteo.button_draft()
            neteo.button_cancel()