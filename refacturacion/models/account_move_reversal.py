from odoo import models,api, fields, _

class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'

    # MIGRACIÓN V19: `helpdesk_account`/`helpdesk_stock_account` (enterprise)
    # llaman `super().reverse_moves(is_modify=is_modify)`; sin declarar el
    # parámetro aquí, la cadena de herencia caía en este override y
    # truena con "TypeError: got an unexpected keyword argument
    # 'is_modify'" al confirmar el wizard de "Nota de crédito" desde una
    # factura de proveedor. Se agrega y se reenvía, igual que el core
    # (`addons/account/wizard/account_move_reversal.py`).
    def reverse_moves(self, is_modify=False):
        r = super(AccountMoveReversal, self).reverse_moves(is_modify=is_modify)

        if self.env.context.get('active_model') == 'account.move':
            credit_note = self.env['account.move'].browse(r['res_id'])
            if not credit_note.movimientos_almacen.filtered(
                lambda x: x.picking_type_code == 'incoming' and x.location_dest_id.id == 69 and x.state == 'assigned'):
                credit_note.create_in()
            credit_note.write({'es_refacturacion': True, 'almacen_refacturacion': 'ALM-9'})

        return r
