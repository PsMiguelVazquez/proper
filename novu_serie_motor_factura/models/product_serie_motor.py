from datetime import datetime
from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class ProductSerieMotor(models.Model):
    _name = 'product.serie.motor'
    _description = 'Número de serie y motor para productos de la categoria motocicleta'

    move_id = fields.Many2one('account.move', string='Factura', store=True)
    invoice_line_id = fields.Many2one('account.move.line', string='Linea Factura')
    product_id = fields.Many2one('product.product', string='Producto', store=True)
    serial_number = fields.Char(string='Número de serie', store=True)
    engine_number = fields.Char(string='Número de motor', store=True)
   
    
    