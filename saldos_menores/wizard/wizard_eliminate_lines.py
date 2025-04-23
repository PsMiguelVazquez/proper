# -*- coding: utf-8 -*-
from collections import defaultdict
from datetime import datetime

from odoo import models, fields, _, api
from odoo.exceptions import UserError, ValidationError
from lxml.objectify import fromstring
class WizardEliminateLine(models.TransientModel):
    _name = 'wizard.eliminate.line'
    _description = 'Wizard eliminate line'
    
    invoice_name = fields.Char('Número')
    invoice_id = fields.Many2one('account.move', 'Movimiento')
    partner_id = fields.Many2one('res.partner','Cliente')
    amount_total = fields.Float('Monto total')
    amount_payed = fields.Float('Monto pagado')
    amount_residual = fields.Float('Monto restante')
    wizard_id = fields.Many2one('wizard.eliminate.balance')
    move_id = fields.Many2one('account.move')
    type = fields.Char('Tipo')