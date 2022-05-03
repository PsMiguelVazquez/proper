# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        return super(AccountMove).action_post()


class Requirement(models.Model):
    _inherit = 'x_client_requirement'

    @api.model
    def create(self, val):
        r = super(Requirement, self).create(val)
        return r


class Proposal(models.Model):
    _inherit = 'x_proposal_purchase'

    @api.model
    def create(self, vals_list):
        r = super(Proposal, self).create(vals_list)
        user = r.x_rel_id.x_order_id.user_id
        odoobot_id = self.env['ir.model.data'].sudo().xmlid_to_res_id("base.partner_root")
        mesagge = "Alertas la siguientes Venta: \n" + str(r.x_rel_id.x_order_id.name)+'tiene nuevas propuestas'
        users_to_send_message = [(4, user.partner_id.id), (4, odoobot_id)]
        messages_to_delete = self.env['mail.message'].sudo().search([('message_type', '=', 'comment'), ('author_id', '=', odoobot_id), ('record_name', '=', 'Alerta de leads')]).unlink()
        channel = self.env['mail.channel'].sudo().search([('name', '=', 'Alerta de leads'), ('channel_partner_ids', 'in', [user.partner_id.id])], limit=1, )
        if not channel:
            # create a new channel
            channel = self.env['mail.channel'].with_context(mail_create_nosubscribe=True).sudo().create({'channel_partner_ids': users_to_send_message, 'public': 'private', 'channel_type': 'chat', 'email_send': False, 'name': f'Alerta de leads'})
        send = channel.sudo().message_post(body=mesagge, author_id=odoobot_id, message_type="comment", subtype_xmlid="mail.mt_comment")
        return r
