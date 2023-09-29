from odoo import models,api, fields, _

class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'

    def reverse_moves(self):
        r = super(AccountMoveReversal, self).reverse_moves()

        if self._context.get('active_model') == 'account.move':
            credit_note = self.env['account.move'].browse(r['res_id'])
            if not credit_note.movimientos_almacen.filtered(
                lambda x: x.picking_type_code == 'incoming' and x.location_dest_id.id == 69 and x.state == 'assigned'):
                credit_note.create_in()
            credit_note.write({'es_refacturacion': True, 'almacen_refacturacion': 'ALM-9'})

        return r