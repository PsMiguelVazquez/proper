# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    adjuntos_so = fields.Many2many('ir.attachment')


    def upload_invoice(self):
        if self.env['account.move'].search([('sale_id','in',self.ids)]).filtered(lambda x: x.state == 'posted'):
            raise UserError(_('No se puede subir una factura externa si la orden ya tiene una factura publicada'))
        if self.filtered(lambda x: x.state != 'sale'):
            raise UserError(_('No se puede subir una factura si el pedido no esta en el estado "Orden de venta"'))
        w = self.env['upload.invoice.wizard'].create({'subtotal': 0.0, 'monto': 0.0, 'tipo':'sale_order', 'margen': 1.0})
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