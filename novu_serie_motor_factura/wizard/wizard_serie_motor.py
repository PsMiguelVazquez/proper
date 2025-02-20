# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from lxml.objectify import fromstring
import logging
_logger = logging.getLogger(__name__)

class WizardSerieMotor(models.TransientModel):
    _name = 'wizard.serie.motor'
    _description = 'Solicitar Número de Serie y Motor al confirmar factura'

    invoice_id = fields.Many2one('account.move', string='Factura')
    line_ids = fields.One2many('wizard.serie.motor.line', 'wizard_id', string='Detalles')

    @api.model
    def _otro_default_get(self, fields_list):
        #_logger.error(f'default_get - Contexto recibido: {self.env.context}')
        #_logger.error(f'default_get')
        res = super().default_get(fields_list)
        
        invoice = self.env['account.move'].browse(self.env.context.get('params', {}).get('id'))
        _logger.error(f'🛠️ Creando wizard para la factura {str(invoice.id)}')
        lines = []
        for line in invoice.invoice_line_ids:
            _logger.error(f'line.product_id.name: {line.product_id.name}, line.product_id.categ_id.name: {line.product_id.categ_id.name}')  
            if line.product_id.categ_id.name == 'MOTOCICLETAS':  # Filtrar por categoría de producto
                lines.append((0, 0, {
                    'product_id': line.product_id.id,
                    'invoice_line_id': line.id,
                }))

        _logger.error(f'lines: {lines}') 
        if lines:
            res.update({'line_ids': lines})
        return res

    def confirm_serial_numbers(self):
        """Guarda los números de serie y motor en las líneas de factura"""
        for line in self.line_ids:
            if not line.serial_number or not line.engine_number:
                raise UserError('Debes ingresar ambos valores.')
            line.invoice_line_id.write({
                'serial_number': line.serial_number,
                'engine_number': line.engine_number,
            })
        return {'type': 'ir.actions.act_window_close'}


class WizardSerieMotorLine(models.TransientModel):
    _name = 'wizard.serie.motor.line'
    _description = 'Líneas del Wizard para Motocicletas'

    wizard_id = fields.Many2one('wizard.serie.motor')
    product_id = fields.Many2one('product.product', string='Producto', readonly=True)
    invoice_line_id = fields.Many2one('account.move.line', string='Línea de Factura', readonly=True)
    serial_number = fields.Char(string='Número de Serie')
    engine_number = fields.Char(string='Número de Motor')