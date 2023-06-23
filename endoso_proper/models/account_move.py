# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class AccountMove(models.Model):
    _inherit = 'account.move'
    cliente_endoso = fields.Many2one('res_partner', string='Cliente de endoso')


    def endosar_factura(self):
        w = self.env['endoso.wizard'].sudo().create({'factura': self.id})
        view = self.env.ref('endoso_proper.view_endoso_wizard_form')
        return {
            'name': _('Endosar Facturas'),
            'type': 'ir.actions.act_window',
            'res_model': 'endoso.wizard',
            'view_mode': 'form',
            'res_id': w.id,
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new'
        }


