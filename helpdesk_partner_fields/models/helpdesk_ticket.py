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
        if not self.env['mail.activity'].search([('res_id', '=', self.id), ('activity_type_id', '=', 4), ('summary', '=', 'Ticket asignado')]):
            self.activity_schedule(
                activity_type_id=4,
                summary="Ticket asignado",
                note='Se le ha asignado el ticket: ' + self.name,
                user_id=activity_user
            )
        return res

    @api.onchange('user_id')
    def on_change_user_id(self):
        activity = self.env['mail.activity'].search(
            [('res_id', '=', self.id.origin), ('activity_type_id', '=', 4), ('summary', '=', 'Ticket asignado')])
        if activity:
            activity_user = self.user_id.id if self.user_id else self.env.uid
            activity.update({'user_id': activity_user})