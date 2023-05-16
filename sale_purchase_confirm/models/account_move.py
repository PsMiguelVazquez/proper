# -*- coding: utf-8 -*-
import base64

from datetime import datetime
import xml.etree.ElementTree as ET
import pytz

from odoo import models, fields, api
from .. import extensions


class AccountMove(models.Model):
    _inherit = 'account.move'
    sale_id = fields.Many2one('sale.order')
    serie = fields.Char('Serie', compute="set_folio")
    folio = fields.Char('Folio', compute="set_folio")
    reason = fields.Char("Motivo")
    tipo_nota = fields.Selection(string='Tipo de nota de crédito', selection=[('01','01 - Descuentos o bonificaciones'),('03','03 - Devolición de mercancia')])
    invoice_datetime = fields.Char('Fecha y hora de facturación', compute='_compute_invoice_datetime')

    def _compute_invoice_datetime(self):
        for record in self:
            self.invoice_datetime = ''
            user_local = pytz.timezone(self.env.user.tz)
            att_xml = self.env['ir.attachment'].search([('res_model','=','account.move'),('res_id','=',record.id),('mimetype','=','application/xml')])
            if att_xml:
                try:
                    path = att_xml[0]._full_path(att_xml.store_fname)
                    tree = ET.parse(path)
                    elements = [el for el in tree.iter()]
                    for element in elements:
                        if 'TimbreFiscalDigital' in element.tag:
                            local_date = user_local.localize(datetime.strptime(element.attrib['FechaTimbrado'], '%Y-%m-%dT%H:%M:%S'), is_dst=None)
                            self.invoice_datetime = local_date.strftime("%d/%m/%Y %H:%M:%S")
                except:
                    continue

    @api.onchange('tipo_nota')
    def onchange_tipo_nota(self):
        for record in self:
            record.x_tipo_de_relacion = record.tipo_nota

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

    def action_post(self):
        if not self.invoice_payment_term_id:
            self.write({'invoice_payment_term_id': self.partner_id.property_supplier_payment_term_id.id})
        return super(AccountMove, self).action_post()

    def remove_other_lines(self, picking_lines):
        self = self.with_context({'check_move_validity': False})
        self.invoice_line_ids = self.invoice_line_ids.filtered(lambda x: x.product_id.id in picking_lines.mapped('product_id.id'))
        self.line_ids.filtered(lambda x: not x.product_id)[0].recompute_tax_line = True
        for linea in picking_lines:
            self.invoice_line_ids.filtered(lambda x: x.product_id == linea.product_id)\
                .write({'quantity': linea.qty_done})
        self._onchange_recompute_dynamic_lines()


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
    uso_cfdi = fields.Selection(string='Uso de CFDI', selection=[('G02', 'G02 - Devoluciones, descuentos o bonificaciones')], default='G02')

    def _prepare_default_reversal(self, move):
        r = super(AccountMoveRevers, self)._prepare_default_reversal(move)
        r['invoice_payment_term_id'] = move.invoice_payment_term_id.id
        r['l10n_mx_edi_payment_policy'] = 'PUE'
        if self.uso_cfdi:
            r['l10n_mx_edi_usage'] = self.uso_cfdi
        return r
    #
    def reverse_moves(self):
        r = super(AccountMoveRevers, self).reverse_moves()
        nota_credito = self.env['account.move'].browse(r['res_id'])
        if nota_credito.l10n_mx_edi_origin:
            origin = nota_credito.l10n_mx_edi_origin.split('|')
            if len(origin) > 1:
                nota_credito.l10n_mx_edi_origin = nota_credito.x_tipo_de_relacion + '|' + origin[1]
            if len(origin) == 1:
                nota_credito.l10n_mx_edi_origin = nota_credito.x_tipo_de_relacion = nota_credito.l10n_mx_edi_origin + '|' + origin[0]
        return r