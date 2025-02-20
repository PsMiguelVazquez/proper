from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

   
    @api.model_create_multi
    def create(self, vals_list):
        _logger.error(f"Entre Create {vals_list}")
        lines = super(AccountMoveLine, self).create(vals_list)

        series_motor = []
        for line in lines:
            _logger.error(f"Create for line in lines {line.product_id.categ_id.name}")
            # Verificar si la línea tiene un producto y si es de la categoría 'MOTOCICLETAS'
            if line.product_id and line.product_id.categ_id.name == 'MOTOCICLETAS' or line.product_id.categ_id.name == 'TRANSPORTE':
                existing_series = self.env['product.serie.motor'].search([('invoice_line_id', '=', line.id), ('product_id', '=', line.product_id.id)])
                _logger.error(f"Create existing_series {existing_series}")
                if not existing_series:
                    for _ in range(int(line.quantity)):  # Crear tantos registros como cantidad en la línea
                        series_motor.append({
                            'move_id': line.move_id.id,
                            'invoice_line_id': line.id,
                            'product_id': line.product_id.id,
                            'serial_number': '',  # Se puede llenar luego
                            'engine_number': '',  # Se puede llenar luego
                        })

        # Si hay registros de serie por crear, se insertan en `product.serie.motor`
        if series_motor:
            self.env['product.serie.motor'].sudo().create(series_motor)

        return lines
        

    def write(self, vals):
        _logger.error(f"Entre Write {vals}")
        res = super(AccountMoveLine,self).write(vals)
        if 'quantity' in vals:
            _logger.error(f"Entre if quantity")
            for line in self:
                if line.product_id and line.product_id.categ_id.name == 'MOTOCICLETAS' or line.product_id.categ_id.name == 'TRANSPORTE':
                    _logger.error(f"Entre if line.product_id and line.product_id.categ_id.name == 'MOTOCICLETAS'")
                    existing_series = self.env['product.serie.motor'].search([('invoice_line_id', '=', line.id), ('product_id', '=', line.product_id.id)])
                    _logger.error(f"existing_series {existing_series}")
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

                        self.env['product.serie.motor'].sudo().create(series_motor)
                        _logger.error(f"series_motor {series_motor}")
                        
                    elif new_count < current_count:
                        # Se eliminan los números de serie sobrantes
                        series_to_remove = existing_series[:current_count - new_count]
                        series_to_remove.unlink()

        return res


    @api.model
    def unlink(self):
        # Detectar si alguna de las líneas está relacionada con tu modelo personalizado
        for line in self:
            # Aquí verificamos si la línea tiene alguna relación con 'product.serie.motor'
            related_motor = self.env['product.serie.motor'].search([('invoice_line_id', '=', line.id),('product_id', '=', line.product_id.id)])
            if related_motor:
                related_motor.unlink()  # Eliminar los registros relacionados de 'product.serie.motor'
        
        # Llamar al método unlink original para eliminar la línea de la factura
        return super(AccountMoveLine, self).unlink()
