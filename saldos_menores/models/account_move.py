# -*- coding: utf-8 -*-
from lxml import etree

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_eliminate_balance(self):
        w = self.env['wizard.eliminate.balance'].create({
            'move_date': datetime.now(),
            'from_date': datetime.now(),
            'to_date': datetime.now(),
            'max_move_balance': 5.0,
        })
        view = self.env.ref('saldos_menores.view_wizard_eliminate_balance_form')
        return {
            'name': _('Eliminación de Saldos Menores'),
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.eliminate.balance',
            'view_mode': 'form',
            'res_id': w.id,
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new'
        }
