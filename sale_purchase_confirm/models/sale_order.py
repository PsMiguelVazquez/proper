# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def conf_credito(self):
        self.write({'x_aprovacion_compras': True, 'x_bloque': False})
        self.action_confirm()


    def conf_ventas(self):
        for record in self:
            registro = self.order_line.filtered(lambda x: x.product_id.virtual_available <= 0).mapped('id')
            if registro != []:
                record['x_aprovar'] = True
            if registro == []:
                # self.action_confirm()
                # record['x_bloqueo']=False
                total = self.partner_id.credit + self.amount_total
                check = self.partner_id.credit_limit >= total if self.payment_term_id.id != 1 else True
                cliente = self.partner_id.x_studio_triple_a
                facturas = self.partner_id.invoice_ids.filtered(lambda x: x.invoice_date_due != False).filtered(
                    lambda x: x.invoice_date_due < datetime.date.today() and x.state == 'posted' and x.payment_state in (
                    'not_paid', 'partial')).mapped('id')
                if cliente and check:
                    record['x_bloqueo'] = False
                    self.action_confirm()
                    record['x_aprovacion_compras'] = True
                else:
                    if self.payment_term_id.id == 1 or not self.payment_term_id:
                        record['x_studio_estado_de_validacin'] = '1'
                        record['x_bloqueo'] = True
                        grupo = self.env['res.groups'].search([['name', '=', 'aprovacion credito']])
                        template = self.env['mail.template'].browse(53)
                        template.write({'email_to': str(grupo.mapped('users.email')).replace('[', '').replace(']', '').replace('\'', '')})
                        template.send_mail(self.id)
                    else:
                        if facturas == []:
                            if self.x_studio_rfc and check:
                                record['x_bloqueo'] = False
                                self.action_confirm()
                                record['x_aprovacion_compras'] = True
                            if not check and self.x_studio_rfc:
                                record['x_studio_estado_de_validacin'] = '2'
                                record['x_bloqueo'] = True
                                grupo = self.env['res.groups'].search([['name', '=', 'aprovacion credito']])
                                template = self.env['mail.template'].browse(53)
                                template.write({'email_to': str(grupo.mapped('users.email')).replace('[', '').replace(']', '').replace('\'', '')})
                                template.send_mail(self.id)
                            if not self.x_studio_rfc:
                                record['x_studio_estado_de_validacin'] = '3'
                                record['x_bloqueo'] = True
                                grupo = self.env['res.groups'].search([['name', '=', 'aprovacion credito']])
                                template = self.env['mail.template'].browse(52)
                                template.write({'email_to': str(grupo.mapped('users.email')).replace('[', '').replace(']', '').replace('\'', '')})
                                template.send_mail(self.id)
                        else:
                            record['x_studio_estado_de_validacin'] = '4'
                            record['x_bloqueo'] = True
                            grupo = self.env['res.groups'].search([['name', '=', 'aprovacion credito']])
                            template = self.env['mail.template'].browse(53)
                            template.write({'email_to': str(grupo.mapped('users.email')).replace('[', '').replace(']', '').replace('\'', '')})
                            template.send_mail(self.id)
                record['x_aprovar'] = False
