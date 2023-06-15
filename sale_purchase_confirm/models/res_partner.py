from odoo import api,models,fields,_
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'
    credit_rest = fields.Float('Credito Disponible', compute='get_credit')
    agente_temporal = fields.Char("Agente temporal")
    x_studio_saldo_vencido = fields.Monetary('Saldo vencido', compute="get_saldo_vencido")
    x_studio_saldo_por_vencer = fields.Monetary('Saldo por vencer', compute="get_x_studio_saldo_por_vencer")


    def get_credit(self):
        for record in self:
            operation = record.credit_limit-record.credit
            record.credit_rest =0 if operation<0 else operation


    def get_saldo_vencido(self):
        for record in self:
            hoy = fields.Date.today()
            invoices = record.invoice_ids.filtered(lambda x: x.invoice_date_due != False)
            # record['x_studio_saldo_vencido'] = sum(
            #     invoices.filtered(lambda x: x.invoice_date_due < hoy and x.state == 'posted').mapped(
            #         'amount_residual_signed'))
            facturas_vencidas_cliente = self.env['account.move'].search([
                ('partner_id', '=', record.id)
                , ('state', '=', 'posted')
                , ('payment_state', 'in', ['not_paid', 'partial'])
                , ('invoice_date_due', '<', fields.Datetime().now())
            ]).filtered(lambda x: not x.x_fecha_pago_pro or x.x_fecha_pago_pro < fields.Date.today())
            record.x_studio_saldo_vencido = sum(facturas_vencidas_cliente.mapped('amount_residual'))

    def get_x_studio_saldo_por_vencer(self):
        for record in self:
            facturas_cliente = self.env['account.move'].search([
                ('partner_id', '=', record.id)
                , ('state', '=', 'posted')
                , ('payment_state', 'in', ['not_paid', 'partial'])
            ])
            record.x_studio_saldo_por_vencer = max(sum(facturas_cliente.mapped('amount_residual')) - record.x_studio_saldo_vencido, 0.00)
