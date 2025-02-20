from odoo import models, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def action_post(self):
        _logger.error("ENTRE ACTION POST 1")
        for invoice in self:
            if invoice.move_type == 'out_invoice':
                _logger.error("ENTRE ACTION POST")
                lines = []
                    
                has_motorcycle = any(line.product_id.categ_id.name == 'MOTOCICLETAS' for line in invoice.invoice_line_ids)
                _logger.error(f"has_motorcycle {has_motorcycle}")
                if has_motorcycle:
                    w = self.env['wizard.serie.motor'].sudo().create({
                    'invoice_id': invoice.id,
                })
                    for line in invoice.invoice_line_ids:
                        _logger.error(f'line.product_id.name: {line.product_id.name}, line.product_id.categ_id.name: {line.product_id.categ_id.name}')  
                        if line.product_id.categ_id.name == 'MOTOCICLETAS':  # Filtrar por categoría de producto
                            lines.append((0, 0, {
                                'wizard_id': w.id,
                                'product_id': line.product_id.id,
                                'invoice_line_id': line.id,
                                'serial_number': '',
                                'engine_number': '',
                                
                            }))
            
                _logger.error(f'lines: {lines}') 
                if lines:
                    w.sudo().write({'line_ids': lines})
                    _logger.error(f'✅ Líneas agregadas al wizard {w.id}')
        if w:  
            _logger.error(f'w: {w}')
            view = self.env.ref('novu_serie_motor_factura.view_wizard_serie_motor_form')
            _logger.error(f'✅ vista {view.id}')
            return {
                'name': _('Registrar número de serie y motor'),
                'type': 'ir.actions.act_window',
                'res_model': 'wizard.serie.motor',
                'view_mode': 'form',
                'res_id': w.id,
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'self'
                
            }
        #return super(AccountMove, self).action_post()