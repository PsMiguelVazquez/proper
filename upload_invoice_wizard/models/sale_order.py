# -*- coding: utf-8 -*-

from odoo import models, fields, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    adjuntos_so = fields.Many2many('ir.attachment')


    def upload_invoice(self):
        print(self)
        w = self.env['upload.invoice.wizard'].create({'subtotal': 0.0, 'monto': 0.0})
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