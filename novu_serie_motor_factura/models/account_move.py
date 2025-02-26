from odoo import models, fields, api, _, exceptions
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    serie_motor = fields.One2many('product.serie.motor', 'move_id', string='Detalles')
    @api.model
    def action_post(self):
        _logger.error("ENTRE ACTION POST 1")
        faltantes = []
        for move in self:
            for line in move.invoice_line_ids:
                _logger.error(f"for line in move.line_ids {line}")
                # Buscar la serie o motor relacionado con la línea de factura
                related_motor = self.env['product.serie.motor'].search([('invoice_line_id', '=', line.id)])
                if related_motor:
                    # Verificar si falta algún dato en 'product.serie.motor'
                    for registro in related_motor:
                        if not registro.serial_number or not registro.engine_number:
                            if line.product_id.name not in faltantes:
                                faltantes.append(line.product_id.name)
        if faltantes:
            faltantes_str = ', '.join(faltantes)
            raise exceptions.UserError(
                "No se puede confirmar la factura. El número de serie y número de motor son obligatorios para los productos {}, verifique la pestaña Número de Serie y Motor, y proporcione los datos faltantes.".format(faltantes_str)
            )
        return super(AccountMove, self).action_post()



    @api.model_create_multi
    def create(self, vals_list):
        moves = super().create(vals_list)
        for move in moves:
            if move.move_type == 'out_invoice' and move.state == 'draft':  # Solo en facturas de cliente en borrador
                move._create_series_motor()
        return moves

        

    def write(self, vals):
        result = super().write(vals)
        for move in self:
            if move.move_type == 'out_invoice' and move.state == 'draft':  # Solo si sigue en borrador
                move._create_series_motor()
        return result

        return res


    def _create_series_motor(self):
        """ Crea las líneas en product.serie.motor si no existen """
        self.ensure_one()
        series_motor = []
        for line in self.invoice_line_ids:
            if line.product_id.categ_id.name in ['MOTOCICLETAS', 'TRANSPORTE']:
                existing_series = self.env['product.serie.motor'].search([
                    ('move_id', '=', self.id),
                    ('invoice_line_id', '=', line.id),
                    ('product_id', '=', line.product_id.id)
                ])
                if not existing_series:
                    for _ in range(int(line.quantity)):
                        series_motor.append({
                            'move_id': self.id,
                            'invoice_line_id': line.id,
                            'product_id': line.product_id.id,
                            'serial_number': '',
                            'engine_number': '',
                        })

                else:
                    current_count = len(existing_series)
                    new_count = int(line.quantity)
                    _logger.error(f"current_count {current_count}, new_count {new_count}")
                    
                    if new_count > current_count:
                        # Se agregan los números de serie faltantes
                        series_motor = [{
                            'move_id': line.move_id.id,
                            'invoice_line_id': line.id,
                            'product_id': line.product_id.id,
                            'serial_number': '',
                            'engine_number': '',
                            
                        } for _ in range(new_count - current_count)]

                        #self.env['product.serie.motor'].sudo().create(series_motor)
                        _logger.error(f"series_motor {series_motor}")
                        
                    elif new_count < current_count:
                        # Se eliminan los números de serie sobrantes
                        series_to_remove = existing_series[:current_count - new_count]
                        series_to_remove.unlink()
                        
        if series_motor:
            self.env['product.serie.motor'].sudo().create(series_motor)
