
from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.payment'

    endosos_count = fields.Integer(compute="_compute_endosos")

    def _compute_endosos(self):
        for record in self: record['endosos_count'] = self.env['endoso.move'].search_count([('payment_id', '=', record.id)])
            

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