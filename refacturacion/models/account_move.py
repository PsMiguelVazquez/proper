from odoo import models,api, fields, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'
    es_refacturacion = fields.Boolean(default=False, string="¿Es refacturación?")
    almacen_refacturacion = fields.Char('Almacén')


    def action_post(self):
        r = super(AccountMove, self).action_post()
        if self.move_type == 'out_refund' and self.es_refacturacion:
            move_in = self.movimientos_almacen.filtered(lambda x: x.picking_type_code == 'incoming' and x.location_dest_id.id == 69 and x.state == 'assigned')
            if move_in:
                move_in.button_validate()

        if self.move_type == 'out_invoice' and self.es_refacturacion:
            move_out = self.movimientos_almacen.filtered(lambda x: x.picking_type_code == 'outgoing' and x.location_id.id == 69 and x.state == 'assigned')
            if move_out:
                move_out.button_validate()
        return r

    def refactura_credito(self):
        moves = self.env['account.move'].browse(self._context.get('active_ids'))
        if moves.filtered(lambda x : not x.es_refacturacion):
            raise UserError('No se puede refacturar si no hay entrada al almacén 9.')
        if len(moves.mapped('partner_id')) > 1:
            raise UserError('No se puede refacturar a dos clientes diferentes en la misma operación.')
        #CREATE ACCOUN_MOVE
        if not moves:
            raise UserError('No se puede hacer refacturación sobre esta factura.')
        if moves.filtered(lambda x: x.move_type != 'out_refund'):
            raise UserError('Sólo se puede utilizar esta acción en una nota de crédito.')
        if moves.filtered(lambda x: x.state != 'posted'):
            raise UserError('Para realizar esta acción, la nota de crédito debe estar en estado publicado.')
        for move in moves:
            product_list = []
            for line in move.invoice_line_ids:
                product_list.append({
                    'name': line.name,
                    'quantity': line.quantity,
                    'product_id': line.product_id,
                    'price_unit': line.price_unit,
                    'tax_ids': line.tax_ids,
                    'product_uom_id': line.product_id.uom_id.id
                })
        partner = moves[0].partner_id
        invoice_dict = {
            'ref': ', '.join(moves.mapped('ref')),
            'x_referencia': ', '.join(moves.mapped('ref')),
            'journal_id': 1,
            'move_type': 'out_invoice',
            'posted_before': False,
            'invoice_payment_term_id': partner.property_payment_term_id.id,
            'partner_id': partner.id,
            'l10n_mx_edi_payment_method_id': partner.x_studio_mtodo_de_pago,
            'l10n_mx_edi_payment_policy': partner.x_nombre_corto_tpago,
            'l10n_mx_edi_usage': partner.x_studio_uso_de_cfdi,
            'invoice_line_ids': product_list,
            'x_studio_almacn': 'ALM-9',
            'es_refacturacion': True,
            'almacen_refacturacion': 'ALM-9',
            'sale_id': moves[0].sale_id
        }
        invoice_id = self.env['account.move'].create(invoice_dict)
        if not moves.movimientos_almacen.filtered(
            lambda x: x.picking_type_code == 'outgoing' and x.location_id.id == 69 and x.state == 'assigned'):
            r = invoice_id.with_context({'sale_id': moves[0].sale_id}).create_out()

        return {
            'name': _('Customer Invoice'),
            'view_mode': 'form',
            'view_id': self.env.ref('account.view_move_form').id,
            'res_model': 'account.move',
            'context': "{'move_type':'out_invoice'}",
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'res_id': invoice_id.id,
            'target': 'current'
        }





    def create_in(self):
        for record in self:
            move_lines_d = []
            for line in record.invoice_line_ids:
                move_line_vals = {
                    'name': line.product_id.name,
                    "product_id": line.product_id.id,
                    "product_uom_qty": line.quantity,
                    "quantity_done": line.quantity,
                    "product_uom": line.product_id.uom_id.id,
                    'location_id': 4,
                    'location_dest_id': 69

                }
                move_lines_d.append((0,0,move_line_vals))
            sale = record.sale_id
            picking = self.env['stock.picking'].create({
                'location_id': 4,
                'origin': sale.name if sale else record.invoice_origin,
                'location_dest_id': 69,
                'partner_id': record.partner_id.id,
                'picking_type_id': 11,
                'immediate_transfer': True,
                'move_type': 'direct',
                'move_lines': move_lines_d,
                'sale_id': sale.id if sale else None,
            })
            # picking.button_validate()
            return picking


    def create_out(self):
        for record in self:
            sale = self._context.get('sale_id')
            move_lines_d = []
            for line in record.invoice_line_ids:
                move_line_vals = {
                    'name': line.product_id.name,
                    "product_id": line.product_id.id,
                    "product_uom_qty": line.quantity,
                    "quantity_done": line.quantity,
                    "product_uom": line.product_id.uom_id.id,
                    'location_id': 69,
                    'location_dest_id': 4,
                }
                move_lines_d.append((0,0,move_line_vals))
            picking = self.env['stock.picking'].create({
                'location_id': 69,
                'origin': sale.name if sale else record.invoice_origin,
                'location_dest_id': 4,
                'partner_id': record.partner_id.id,
                'picking_type_id': 12,
                'immediate_transfer': True,
                'move_type': 'direct',
                'move_lines': move_lines_d,
                'sale_id': sale.id if sale else 0,
            })
            # picking.button_validate()
            return picking

