from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    serie_motor_ids = fields.One2many(
        'product.serie.motor', 
        'invoice_line_id', 
        string="Series de Motor"
    )
    
    @api.model
    def unlink(self):
        deleted_lines = []
        for line in self:
            related_motor = self.env['product.serie.motor'].search([('invoice_line_id', '=', line.id),('product_id', '=', line.product_id.id)])
            if related_motor:
                deleted_lines.append(line.id)
                related_motor.unlink() 

        
        return super(AccountMoveLine, self).unlink()
