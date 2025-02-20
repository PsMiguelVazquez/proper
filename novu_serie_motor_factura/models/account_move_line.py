from odoo import models, fields

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    serial_number = fields.Char(string="Número de Serie")
    engine_number = fields.Char(string="Número de Motor")