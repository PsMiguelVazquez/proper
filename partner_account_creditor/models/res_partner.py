# -*- coding: utf-8 -*-

from odoo import models, fields, api

class res_partner_fields(models.Model):
    _inherit = 'res.partner'
    property_account_creditor = fields.Many2one('account.account', 'Cuenta de acreedor')
