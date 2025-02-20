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