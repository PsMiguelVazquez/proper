# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
from .. import extensions
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    total_in_text = fields.Char(compute='set_amount_text', string='Total en letra')
    state = fields.Selection([('draft', 'Quotation'), ('sent', 'Quotation Sent'), ('sale_conf', 'Validación ventas'), ('purchase_conf', 'Validación compras'), ('credito_conf', 'Validación credito'), ('sale', 'Sales Order'), ('done', 'Locked'), ('cancel', 'Cancelled'), ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    purchase_ids = fields.Many2many('purchase.order', string='OC', readonly=True)
    partner_child = fields.Many2one('res.partner', 'Solicitante')

    @api.onchange('partner_child')
    def set_partner_id(self):
        for record in self:
            if record.partner_child:
                if record.partner_child.parent_id:
                    record.partner_id = record.partner_child.parent_id
                else:
                    record.partner_id = record.partner_child
                record.x_studio_cliente_de_marketplace = record.partner_child.name

    def update_stock(self):
        for rec in self.order_line:
            rec.get_stock()

    @api.model
    def create(self, vals):
        if 'user_id' in vals:
            vals['user_id'] = self.env.user.id
        return super(SaleOrder, self).create(vals)

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

    def conf_purchase(self):
        total = self.partner_id.credit + self.amount_total
        check = self.partner_id.credit_limit >= total if self.payment_term_id.id != 1 else True
        cliente = self.partner_id.x_studio_triple_a
        if cliente and check:
            self.write({'x_bloqueo': False, 'x_aprovacion_compras': True})
            self.action_confirm()
        else:
            self.write({'state': 'credito_conf'})

    def conf_ventas(self):
        registro = self.order_line.filtered(lambda x: x.product_id.virtual_available <= 0).mapped('id')
        if registro != []:
            self.write({'x_aprovar': True, 'state': 'purchase_conf'})
        if registro == []:
            total = self.partner_id.credit + self.amount_total
            check = self.partner_id.credit_limit >= total if self.payment_term_id.id != 1 else True
            cliente = self.partner_id.x_studio_triple_a
            facturas = self.partner_id.invoice_ids.filtered(lambda x: x.invoice_date_due != False).filtered(lambda x: x.invoice_date_due < fields.date.today() and x.state == 'posted' and x.payment_state in ('not_paid', 'partial')).mapped('id')
            if cliente and check:
                self.write({'x_bloqueo': False, 'x_aprovacion_compras': True})
                self.action_confirm()
            else:
                self.write({'state': 'credito_conf'})
                if self.payment_term_id.id == 1 or not self.payment_term_id:
                    self.write({'x_bloqueo': True, 'x_studio_estado_de_validacin': '1'})
                    grupo = self.env['res.groups'].search([['name', '=', 'aprovacion credito']])
                    template = self.env['mail.template'].browse(53)
                    template.write({'email_to': str(grupo.mapped('users.email')).replace('[', '').replace(']', '').replace('\'', '')})
                    #template.send_mail(self.id)
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
                            #template.send_mail(self.id)
                        if not self.x_studio_rfc:
                            self.write({'x_bloqueo': False, 'x_studio_estado_de_validacin': '3'})
                            grupo = self.env['res.groups'].search([['name', '=', 'aprovacion credito']])
                            template = self.env['mail.template'].browse(52)
                            template.write({'email_to': str(grupo.mapped('users.email')).replace('[', '').replace(']', '').replace('\'', '')})
                            #template.send_mail(self.id)
                    else:
                        self.write({'x_bloqueo': False, 'x_studio_estado_de_validacin': '4'})
                        grupo = self.env['res.groups'].search([['name', '=', 'aprovacion credito']])
                        template = self.env['mail.template'].browse(53)
                        template.write({'email_to': str(grupo.mapped('users.email')).replace('[', '').replace(']', '').replace('\'', '')})
                        #template.send_mail(self.id)
            self.write({'x_aprovar': False})
            
    def action_confirm_sale(self):
        registro = self.order_line.filtered(lambda x: x.product_id.virtual_available <= 0).mapped('id')
        if registro != []:
            self.write({'x_aprovar': True, 'state': 'sale_conf'})
        if registro == []:
            self.write({'x_aprovar': False})
            total = -(self.partner_id.credit) + self.amount_total
            check = self.partner_id.credit_limit >= total if self.payment_term_id.id != 1 else True
            cliente = self.partner_id.x_studio_triple_a
            facturas = self.partner_id.invoice_ids.filtered(lambda x: x.invoice_date_due != False).filtered(
                lambda x: x.invoice_date_due < fields.date.today() and x.state == 'posted' and x.payment_state in ('not_paid', 'partial')).mapped('id')
            if cliente and check:
                self.write({'x_bloqueo': False, 'x_aprovacion_compras': True})
                return self.action_confirm()
            else:
                self.write({'state':'credito_conf'})
                if self.payment_term_id.id == 1 or not self.payment_term_id:
                    self.write({'x_bloqueo': True, 'x_studio_estado_de_validacin': '1'})
                    grupo = self.env['res.groups'].search([['name', '=', 'aprovacion credito']])
                    template = self.env['mail.template'].browse(53)
                    template.write({'email_to': str(grupo.mapped('users.email')).replace('[', '').replace(']','').replace('\'', '')})
                    #template.send_mail(self.id)
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
                            #template.send_mail(self.id)
                        if not self.x_studio_rfc:
                            self.write({'x_bloqueo': True, 'x_studio_estado_de_validacin': '3'})
                            grupo = self.env['res.groups'].search([['name', '=', 'aprovacion credito']])
                            template = self.env['mail.template'].browse(52)
                            template.write({'email_to': str(grupo.mapped('users.email')).replace('[', '').replace(']', '').replace('\'', '')})
                            #template.send_mail(self.id)
                    else:
                        self.write({'x_bloqueo': True, 'x_studio_estado_de_validacin': '4'})
                        grupo = self.env['res.groups'].search([['name', '=', 'aprovacion credito']])
                        template = self.env['mail.template'].browse(53)
                        template.write({'email_to': str(grupo.mapped('users.email')).replace('[', '').replace(']','').replace('\'', '')})
                        #stemplate.send_mail(self.id)

    def action_view_invoice(self):
        self.invoice_ids.write({'sale_id': self.id})
        return super(SaleOrder, self).action_view_invoice()

    @api.onchange('partner_id', 'partner_child')
    def get_partner(self):
        for record in self:
            res = {}
            group = self.env.ref('sales_team.group_sale_salesman')
            group_s = self.env.ref('sales_team.group_sale_salesman_all_leads')
            grup_ss = self.env.ref('sales_team.group_sale_manager')
            if self.env.user.id in group.users.ids and not self.env.user.id in group_s.users.ids and not self.env.user.id in grup_ss.users.ids:
                partner = self.env['res.partner'].search([['x_nombre_agente_venta', '=', self.env.user.name]])
            else:
                partner = self.env['res.partner'].search([])
            res = {'domain': {'partner_id': [['id', 'in', partner.ids+partner.mapped('child_ids').ids]], 'partner_child': [['id', 'in', partner.ids+partner.mapped('child_ids').ids]]}}
            return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    existencia = fields.Char('Cantidades', compute='get_stock')

    @api.onchange('price_unit', 'product_id')
    def limit_price(self):
        for record in self:
            valor = 0
            if record.product_id:
                if record.order_id.x_studio_nivel:
                    margen = record.product_id.x_fabricante['x_studio_margen_' + str(record.order_id.x_studio_nivel)] if record.product_id.x_fabricante else 20
                    valor = record.product_id.standard_price / ((100 - margen) / 100)
                else:
                    margen = 20
                    valor = record.product_id.standard_price / ((100 - margen) / 100)
                if valor!=0:
                    if record.price_unit!=0:
                        if valor > record.price_unit:
                            raise UserError('No puede modificar el precio de venta')
            record['x_nuevo_precio'] = round(valor + .5)
            record.product_id.write({'list_price': round(valor + .5)})

    @api.depends('product_id')
    def get_stock(self):
        for record in self:
            existencia = ""
            if record.product_id:
                zero = sum(record.product_id.stock_quant_ids.filtered(lambda x: x.location_id.id == 187).mapped('available_quantity'))
                zero1 = sum(record.product_id.stock_quant_ids.filtered(lambda x: x.location_id.id == 187).mapped('reserved_quantity'))
                # one=sum(record.product_id.stock_quant_ids.filtered(lambda x:x.location_id.id==18).mapped('available_quantity'))
                market = sum(record.product_id.stock_quant_ids.filtered(lambda x: x.location_id.id == 80).mapped('available_quantity'))
                market1 = sum(record.product_id.stock_quant_ids.filtered(lambda x: x.location_id.id == 80).mapped('reserved_quantity'))
                existencia = "<table><thead><tr><th>A-0</th><th>A14</th></tr><tr><th>D/R</th><th>D/R</th></tr></thead><tbody><tr><td>" + str(int(zero)) + "/" + str(int(zero1)) + "</td><td>" + str(int(market)) + "/" + str(int(market1)) + "</td></tr></tbody>"
            record.existencia = existencia


class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'

    def reverse_moves(self):
        r = super(AccountMoveReversal, self).reverse_moves()
        move = self.env['account.move'].browse(r['res_id'])
        move.write({'reason': self.reason})
        return r


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def create_invoices(self):
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        validacion = False
        for line in sale_orders.order_line:
            if line.product_id.virtual_available > 0:
                validacion = True
        if validacion:
            super(SaleAdvancePaymentInv, self).create_invoices()
        else:
            raise UserError('No hay stock')
