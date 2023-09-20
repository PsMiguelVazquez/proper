# -*- coding: utf-8 -*-
from lxml import etree

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class AccountMove(models.Model):
    _inherit = 'account.move'
    amount_to_eliminate = fields.Monetary('Saldo', computed='_get_amount_to_eliminate')

    @api.depends('amount_total_unsigned','x_importe_pagado')
    def _get_amount_to_eliminate(self):
        for record in self:
            record.amount_to_eliminate = record.amount_total_unsigned - record.x_importe_pagado

    def action_eliminate_balance(self):
        view = self.env.ref('saldos_menores.view_wizard_eliminate_balance_form')
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
