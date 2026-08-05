from odoo import api,models,fields,_
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'
    credit_rest = fields.Float('Credito Disponible', compute='get_credit')
    # MIGRACIÓN V19: se restaura - se había borrado por error en una
    # limpieza de la migración, pero `get_partner()` (`models/sale_order.py`)
    # lo sigue usando en su dominio de búsqueda; sin el campo, el compute
    # truena con "KeyError: 'agente_temporal'" para cualquier vendedor sin
    # permiso de "ver todos los leads"/gerente al abrir una orden de venta.
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
            # MIGRACIÓN V19: `x_fecha_pago_pro` se formalizó como campo real
            # en `account_move_proper`, pero declarar esa dependencia aquí
            # crearía un ciclo (`account_move_proper` ya depende de este
            # módulo por `x_studio_n_orden_de_compra`). Se lee de forma
            # defensiva: si `account_move_proper` no está instalado, se
            # ignora el filtro adicional de fecha de pago probable.
            domain = [
                ('partner_id', '=', record.id),
                ('state', '=', 'posted'),
                ('payment_state', 'in', ['not_paid', 'partial']),
                ('invoice_date_due', '<', fields.Datetime().now()),
            ]
            facturas_vencidas_cliente = self.env['account.move'].search(domain)
            if 'x_fecha_pago_pro' in self.env['account.move']._fields:
                facturas_vencidas_cliente = facturas_vencidas_cliente.filtered(
                    lambda x: not x.x_fecha_pago_pro or x.x_fecha_pago_pro < fields.Date.today())
            record.x_studio_saldo_vencido = sum(facturas_vencidas_cliente.mapped('amount_residual'))

    def get_x_studio_saldo_por_vencer(self):
        for record in self:
            facturas_cliente = self.env['account.move'].search([
                ('partner_id', '=', record.id)
                , ('state', '=', 'posted')
                , ('payment_state', 'in', ['not_paid', 'partial'])
            ])
            record.x_studio_saldo_por_vencer = max(sum(facturas_cliente.mapped('amount_residual')) - record.x_studio_saldo_vencido, 0.00)
