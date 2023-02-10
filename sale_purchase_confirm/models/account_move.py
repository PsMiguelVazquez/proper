# -*- coding: utf-8 -*-
from odoo import models, fields, api
from .. import extensions


class AccountMove(models.Model):
    _inherit = 'account.move'
    sale_id = fields.Many2one('sale.order')
    serie = fields.Char('Serie', compute="set_folio")
    folio = fields.Char('Folio', compute="set_folio")
    reason = fields.Char("Motivo")

    @api.depends('name')
    def set_folio(self):
        for record in self:
            serie = ""
            folio = ""
            if record.name and len(record.name)>1:
                tmp = record.name.split('/') if record.name else ""
                for i in range(len(tmp)):
                    if i == (len(tmp) - 1):
                        folio = str(int(tmp[i]))
                    else:
                        serie = serie + (tmp[i] + '/')
            record.serie = serie
            record.folio = folio



    #def action_post(self):
    #    return super(AccountMove).action_post()


class Requirement(models.Model):
    _name = 'x_client_requirement'

    @api.model
    def create(self, val):
        r = super(Requirement, self).create(val)
        return r


class Proposal(models.Model):
    _name = 'x_proposal_purchase'

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


class AccountMoveRevers(models.TransientModel):
    _inherit = 'account.move.reversal'

    def _prepare_default_reversal(self, move):
        r = super(AccountMoveRevers, self)._prepare_default_reversal(move)
        r['invoice_payment_term_id'] = move.invoice_payment_term_id.id
        return r
