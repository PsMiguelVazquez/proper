# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
from .. import extensions
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    total_in_text = fields.Char(compute='set_amount_text', string='Total en letra')

    @api.depends('amount_total')
    def set_amount_text(self):
        for record in self:
            if record.amount_total:
                record.total_in_text = extensions.text_converter.number_to_text_es(record.amount_total)
            else:
                record.total_in_text = extensions.text_converter.number_to_text_es(0)

    def conf_credito(self):
        self.write({'x_aprovacion_compras': True, 'x_bloqueo': False})
        self.action_confirm()

    def conf_ventas(self):
        registro = self.order_line.filtered(lambda x: x.product_id.virtual_available <= 0).mapped('id')
        if registro != []:
            self.write({'x_aprovar': True})
        if registro == []:
            total = self.partner_id.credit + self.amount_total
            check = self.partner_id.credit_limit >= total if self.payment_term_id.id != 1 else True
            cliente = self.partner_id.x_studio_triple_a
            facturas = self.partner_id.invoice_ids.filtered(lambda x: x.invoice_date_due != False).filtered(lambda x: x.invoice_date_due < fields.date.today() and x.state == 'posted' and x.payment_state in ('not_paid', 'partial')).mapped('id')
            if cliente and check:
                self.write({'x_bloqueo': False, 'x_aprovacion_compras': True})
                self.action_confirm()
            else:
                if self.payment_term_id.id == 1 or not self.payment_term_id:
                    self.write({'x_bloqueo': True, 'x_studio_estado_de_validacin': '1'})
                    grupo = self.env['res.groups'].search([['name', '=', 'aprovacion credito']])
                    template = self.env['mail.template'].browse(53)
                    template.write({'email_to': str(grupo.mapped('users.email')).replace('[', '').replace(']', '').replace('\'', '')})
                    template.send_mail(self.id)
                else:
                    if facturas == []:
                        if self.x_studio_rfc and check:
                            self.write({'x_bloqueo': False, 'x_aprovacion_compras': True})
                            self.action_confirm()
                        if not check and self.x_studio_rfc:
                            self.write({'x_bloqueo': True, 'x_studio_estado_de_validacin': '2'})
                            grupo = self.env['res.groups'].search([['name', '=', 'aprovacion credito']])
                            template = self.env['mail.template'].browse(53)
                            template.write({'email_to': str(grupo.mapped('users.email')).replace('[', '').replace(']', '').replace('\'', '')})
                            template.send_mail(self.id)
                        if not self.x_studio_rfc:
                            self.write({'x_bloqueo': False, 'x_studio_estado_de_validacin': '3'})
                            grupo = self.env['res.groups'].search([['name', '=', 'aprovacion credito']])
                            template = self.env['mail.template'].browse(52)
                            template.write({'email_to': str(grupo.mapped('users.email')).replace('[', '').replace(']', '').replace('\'', '')})
                            template.send_mail(self.id)
                    else:
                        self.write({'x_bloqueo': False, 'x_studio_estado_de_validacin': '4'})
                        grupo = self.env['res.groups'].search([['name', '=', 'aprovacion credito']])
                        template = self.env['mail.template'].browse(53)
                        template.write({'email_to': str(grupo.mapped('users.email')).replace('[', '').replace(']', '').replace('\'', '')})
                        template.send_mail(self.id)
            self.write({'x_aprovar': False})
            
    def action_confirm_sale(self):
        registro = self.order_line.filtered(lambda x: x.product_id.virtual_available <= 0).mapped('id')
        if registro != []:
            self.write({'x_aprovar': True})
        if registro == []:
            self.write({'x_aprovar': False})
            total = self.partner_id.credit + self.amount_total
            check = self.partner_id.credit_limit >= total if self.payment_term_id.id != 1 else True
            cliente = self.partner_id.x_studio_triple_a
            facturas = self.partner_id.invoice_ids.filtered(lambda x: x.invoice_date_due != False).filtered(
                lambda x: x.invoice_date_due < fields.date.today() and x.state == 'posted' and x.payment_state in ('not_paid', 'partial')).mapped('id')
            if cliente and check:
                self.write({'x_bloqueo': False, 'x_aprovacion_compras': True})
                return self.action_confirm()
            else:
                if self.payment_term_id.id == 1 or not self.payment_term_id:
                    self.write({'x_bloqueo': True, 'x_studio_estado_de_validacin': '1'})
                    grupo = self.env['res.groups'].search([['name', '=', 'aprovacion credito']])
                    template = self.env['mail.template'].browse(53)
                    template.write({'email_to': str(grupo.mapped('users.email')).replace('[', '').replace(']','').replace('\'', '')})
                    template.send_mail(self.id)
                else:
                    if facturas == []:
                        if self.x_studio_rfc and check:
                            self.write({'x_bloqueo': False, 'x_aprovacion_compras': True})
                            return self.action_confirm()
                        if not check and self.x_studio_rfc:
                            self.write({'x_bloqueo': True, 'x_studio_estado_de_validacin': '2'})
                            grupo = self.env['res.groups'].search([['name', '=', 'aprovacion credito']])
                            template = self.env['mail.template'].browse(53)
                            template.write({'email_to': str(grupo.mapped('users.email')).replace('[', '').replace(']','').replace('\'', '')})
                            template.send_mail(self.id)
                        if not self.x_studio_rfc:
                            self.write({'x_bloqueo': True, 'x_studio_estado_de_validacin': '3'})
                            grupo = self.env['res.groups'].search([['name', '=', 'aprovacion credito']])
                            template = self.env['mail.template'].browse(52)
                            template.write({'email_to': str(grupo.mapped('users.email')).replace('[', '').replace(']', '').replace('\'', '')})
                            template.send_mail(self.id)
                    else:
                        self.write({'x_bloqueo': True, 'x_studio_estado_de_validacin': '4'})
                        grupo = self.env['res.groups'].search([['name', '=', 'aprovacion credito']])
                        template = self.env['mail.template'].browse(53)
                        template.write({'email_to': str(grupo.mapped('users.email')).replace('[', '').replace(']','').replace('\'', '')})
                        template.send_mail(self.id)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('price_unit')
    def limit_price(self):
        for record in self:
            if record.product_id:
                if record.x_nuevo_precio>record.price_unit:
                    raise UserError('No puede modificar el precio de venta')

