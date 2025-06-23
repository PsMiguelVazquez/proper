import logging
from odoo import models, fields
_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    id_usuario_validador = fields.Many2one('res.users', string='Valido por')

    def button_validate(self):
        if self.env.context.get('skip_validation_wizard'):
            return super().button_validate()

        return {
            'name': 'Confirmar Validación',
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.usuario.valida.traslado',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_user_id': self.env.user.id,
                'active_id': self.id,
            }
        }