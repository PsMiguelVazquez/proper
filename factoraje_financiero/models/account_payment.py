import logging
from odoo import models, fields
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.payment'

    endosos_count = fields.Integer(compute="_compute_endosos")

    def action_view_endosos(self):
        self.ensure_one()
        reconciled_lines = self._get_all_reconciled_lines()
        endosos = self.env['endoso.move'].search([('invoice_line_ids', 'in', reconciled_lines.ids)])

        return {
            'type': 'ir.actions.act_window',
            'name': 'Endosos',
            'view_mode': 'list,form',
            'res_model': 'endoso.move',
            'domain': [('id', 'in', endosos.ids)],
            'context': dict(self.env.context),
        }

    def _compute_endosos(self):
        Endoso = self.env['endoso.move']
        for payment in self:
            reconciled_lines = payment._get_all_reconciled_lines()
            endosos = Endoso.search([('invoice_line_ids', 'in', reconciled_lines.ids)])
            payment.endosos_count = len(endosos)

    def _get_all_reconciled_lines(self):
        self.ensure_one()
        lines = self.move_id.line_ids

        reconciled_lines = self.env['account.move.line']

        for line in lines:
            if line.credit > 0:
                matched = line.matched_debit_ids.mapped('debit_move_id')
                reconciled_lines |= matched
            elif line.debit > 0:
                matched = line.matched_credit_ids.mapped('credit_move_id')
                reconciled_lines |= matched

            reconciled_lines |= line  # incluir la línea original también

        return reconciled_lines

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
