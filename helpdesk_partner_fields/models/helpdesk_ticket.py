from odoo import api, models, fields


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    @api.onchange('sale_order_id')
    def _get_default_partner_id(self):

        if self.sale_order_id:
            self.partner_id = self.sale_order_id.partner_id

    def write(self, vals):
        res = super(HelpdeskTicket, self).write(vals)
        activity_user = self.user_id.id if self.user_id else self.env.uid
        # MIGRACIÓN V19: `activity_type_id=4` es un id hardcodeado de la base
        # de producción de 15.0. Se reemplaza por la referencia estable
        # `mail.mail_activity_data_todo` ("Para hacer"), el tipo de actividad
        # genérico al que ese id corresponde de forma consistente en una
        # instalación estándar (email=1, call=2, meeting=3, todo=4).
        activity_type = self.env.ref('mail.mail_activity_data_todo')
        if not self.env['mail.activity'].search([('res_id', '=', self.id), ('activity_type_id', '=', activity_type.id), ('summary', '=', 'Ticket asignado')]):
            self.activity_schedule(
                activity_type_id=activity_type.id,
                summary="Ticket asignado",
                note='Se le ha asignado el ticket: ' + self.name,
                user_id=activity_user
            )
        return res

    @api.onchange('user_id')
    def on_change_user_id(self):
        activity_type = self.env.ref('mail.mail_activity_data_todo')
        activity = self.env['mail.activity'].search(
            [('res_id', '=', self.id.origin), ('activity_type_id', '=', activity_type.id), ('summary', '=', 'Ticket asignado')])
        if activity:
            activity_user = self.user_id.id if self.user_id else self.env.uid
            activity.update({'user_id': activity_user})
