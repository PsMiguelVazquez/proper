from odoo import models, fields

class WizardUsuarioValidaTraslado(models.TransientModel):
    _name = 'wizard.usuario.valida.traslado'
    _description = 'Wizard para validar traslado con usuario'

    user_id = fields.Many2one('res.users', string='Usuario que valida', required=True)

    def confirm_validation(self):
        picking = self.env['stock.picking'].browse(self._context.get('active_id'))
        picking.write({'id_usuario_validador': self.user_id.id})  # campo personalizado si deseas
        return picking.with_context(skip_validation_wizard=True).button_validate()

    def action_cancel(self):
        return {'type': 'ir.actions.act_window_close'}