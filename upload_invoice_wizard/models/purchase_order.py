# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    adjuntos_po = fields.Many2many('ir.attachment')


    def upload_invoice(self):
        if self.env['account.move'].search([('invoice_origin','in',self.mapped('name')),('move_type','=','in_invoice')]).filtered(lambda x: x.state == 'posted'):
            raise UserError(_('No se puede subir una factura externa si la orden ya tiene una factura publicada'))
        if self.filtered(lambda x: x.state != 'purchase'):
            raise UserError(_('No se puede subir una factura si el pedido no esta en el estado "Orden de compra"'))
        w = self.env['upload.invoice.wizard'].create({'subtotal': 0.0, 'monto': 0.0, 'tipo': 'purchase_order'})
        view = self.env.ref('upload_invoice_wizard.view_upload_invoice_sale_form')
        return {
            'name': _('Asignar Facturas'),
            'type': 'ir.actions.act_window',
            'res_model': 'upload.invoice.wizard',
            'view_mode': 'form',
            'res_id': w.id,
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new'
        }