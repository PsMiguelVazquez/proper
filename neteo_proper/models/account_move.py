# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class AccountMove(models.Model):
    _inherit = 'account.move'

    def compensar_factura(self):
        w = self.env['neteo.wizard'].sudo().create({'factura_cliente': self.id
                                                       , 'cliente':self.partner_id.id
                                                       , 'amount_cliente': self.amount_residual
                                                    })
        view = self.env.ref('neteo_proper.view_neteo_wizard_form')
        return {
            'name': _('Pagar Facturas'),
            'type': 'ir.actions.act_window',
            'res_model': 'neteo.wizard',
            'view_mode': 'form',
            'res_id': w.id,
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new'
        }

