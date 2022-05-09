# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime


class SaleOrder(models.Model):
    _inherit = 'sale.order'

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
            facturas = self.partner_id.invoice_ids.filtered(lambda x: x.invoice_date_due != False).filtered(lambda x: x.invoice_date_due < datetime.date.today() and x.state == 'posted' and x.payment_state in ('not_paid', 'partial')).mapped('id')
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
            
    def action_confirm(self):
        registro = self.order_line.filtered(lambda x: x.product_id.virtual_available <= 0).mapped('id')
        if registro != []:
            self.write({'x_aprovar': True})
        if registro == []:
            self.write({'x_aprovar': False})
            total = self.partner_id.credit + self.amount_total
            check = self.partner_id.credit_limit >= total if self.payment_term_id.id != 1 else True
            cliente = self.partner_id.x_studio_triple_a
            facturas = self.partner_id.invoice_ids.filtered(lambda x: x.invoice_date_due != False).filtered(
                lambda x: x.invoice_date_due < datetime.date.today() and x.state == 'posted' and x.payment_state in ('not_paid', 'partial')).mapped('id')
            if cliente and check:
                self.write({'x_bloqueo': False, 'x_aprovacion_compras': True})
                return super(SaleOrder, self).action_confirm()
            else:
                if self.payment_term_id.id == 1 or not self.payment_term_id:
                    self.write({'x_bloqueo': True, 'x_studio_estado_de_validacin': '1'})
                    grupo = env['res.groups'].search([['name', '=', 'aprovacion credito']])
                    template = env['mail.template'].browse(53)
                    template.write({'email_to': str(grupo.mapped('users.email')).replace('[', '').replace(']','').replace('\'', '')})
                    template.send_mail(self.id)
                else:
                    if facturas == []:
                        if self.x_studio_rfc and check:
                            self.write({'x_bloqueo': False, 'x_aprovacion_compras': True})
                            return super(SaleOrder, self).action_confirm()
                        if not check and self.x_studio_rfc:
                            self.write({'x_bloqueo': True, 'x_studio_estado_de_validacin': '2'})
                            grupo = env['res.groups'].search([['name', '=', 'aprovacion credito']])
                            template = env['mail.template'].browse(53)
                            template.write({'email_to': str(grupo.mapped('users.email')).replace('[', '').replace(']','').replace('\'', '')})
                            template.send_mail(self.id)
                        if not self.x_studio_rfc:
                            self.write({'x_bloqueo': True, 'x_studio_estado_de_validacin': '3'})
                            grupo = env['res.groups'].search([['name', '=', 'aprovacion credito']])
                            template = env['mail.template'].browse(52)
                            template.write({'email_to': str(grupo.mapped('users.email')).replace('[', '').replace(']', '').replace('\'', '')})
                            template.send_mail(self.id)
                    else:
                        self.write({'x_bloqueo': True, 'x_studio_estado_de_validacin': '4'})
                        grupo = env['res.groups'].search([['name', '=', 'aprovacion credito']])
                        template = env['mail.template'].browse(53)
                        template.write({'email_to': str(grupo.mapped('users.email')).replace('[', '').replace(']','').replace('\'', '')})
                        template.send_mail(self.id)
