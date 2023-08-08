
from odoo import fields,models, _
from datetime import datetime
from odoo.exceptions import UserError

class AccountEdiFormat(models.Model):
    _inherit = 'account.move'
    factoring_amount = fields.Float('Monto por factoraje')


    def view_financial_factoring_wizard(self):
        # if self.env['account.move'].search([('sale_id','in',self.ids)]).filtered(lambda x: x.state == 'posted'):
        #     raise UserError(_('No se puede subir una factura externa si la orden ya tiene una factura publicada'))
        p_bills = self.env.context.get('active_ids')
        partner_id = self.env['account.move'].browse(self.env.context.get('active_ids')).mapped('partner_id')
        if len(partner_id) > 1:
            raise UserError('No se puede hacer factoraje para facturas de diferentes clientes')
        w = self.env['factoraje.financiero.wizard'].create({
            'partner_id': partner_id.id,
            'amount_total': 0.0,
            'partner_bills': p_bills,
            'payment_date': datetime.now(),
            'currency': self.env.company.currency_id.id
        })
        view = self.env.ref('factoraje_financiero.view_factoraje_wizard')
        return {
            'name': _('Factoraje'),
            'type': 'ir.actions.act_window',
            'res_model': 'factoraje.financiero.wizard',
            'view_mode': 'form',
            'res_id': w.id,
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new'
        }
        print(self)