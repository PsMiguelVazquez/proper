from odoo import api,models,fields,_
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'
    credit_rest = fields.Float('Credito Disponible', compute='get_credit')
    agente_temporal = fields.Char("Agente temporal")
    def get_credit(self):
        for record in self:
            operation = record.credit_limit-record.credit
            record.credit_rest =0 if operation<0 else operation
