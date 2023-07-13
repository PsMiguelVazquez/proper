# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class Neteo(models.Model):
    _name = 'neteo.move'
    _inherits = {'account.move': 'move_id'}
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Neteo"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['move_type'] = 'entry'
            # if 'journal_id' not in vals:
            #     vals['journal_id'] = self.move_id._get_default_journal().id
            if 'currency_id' not in vals:
                journal = self.env['account.journal'].browse(vals['journal_id'])
                vals['currency_id'] = journal.currency_id.id or journal.company_id.currency_id.id
        neteos = super().create(vals_list)
        return neteos