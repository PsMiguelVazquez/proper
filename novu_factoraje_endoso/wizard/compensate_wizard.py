# -*- coding: utf-8 -*-
from collections import defaultdict
from datetime import datetime

from odoo import models, fields, _, api
from odoo.exceptions import UserError, ValidationError
from lxml.objectify import fromstring
class CompensateWizard(models.TransientModel):
    _inherit = 'account.payment.register'
    _description = 'Muestra un wizard para el proceso de compensación.'

    amount_residual_compensation = fields.Float('Monto restante compensación', compute='_compute_monto_compensacion')
    hide_button_payment_register = fields.Boolean(default=False)

    @api.depends('partner_bills', 'amount_factor_bill')
    def _compute_monto_compensacion(self):
        for record in self:
            record['amount_residual_compensation'] = record.amount_factor_bill - sum(record.partner_bills.mapped('porcent_assign'))

    def compensate(self):
        for inv in self.partner_bills:
            inv.write({'factoring_amount': inv.porcent_assign})
        r = self.create_neteo()
        return r

