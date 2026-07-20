# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    x_equipo_ventas_fact = fields.Char(
        string='Equipo(s) de ventas', compute='_compute_x_equipo_ventas_fact')
    x_total_adeudado = fields.Float(
        string='Importe total adeudado de facturas', compute='_compute_x_total_adeudado')
    x_total_facturas = fields.Float(
        string='Importe total  de las facturas', compute='_compute_x_total_facturas')
    x_total_pagado_facturas = fields.Float(
        string='Importe pagado de facturas', compute='_compute_x_total_pagado_facturas')
    x_vendedores = fields.Char(
        string='Vendedor(es)', compute='_compute_x_vendedores')

    @api.depends('reconciled_invoice_ids')
    def _compute_x_equipo_ventas_fact(self):
        for record in self:
            record.x_equipo_ventas_fact = ','.join(
                record.reconciled_invoice_ids.mapped('invoice_user_id.sale_team_id.name'))

    @api.depends('reconciled_invoice_ids')
    def _compute_x_total_adeudado(self):
        for record in self:
            record.x_total_adeudado = sum(record.reconciled_invoice_ids.mapped('amount_residual'))

    @api.depends('reconciled_invoice_ids')
    def _compute_x_total_facturas(self):
        for record in self:
            record.x_total_facturas = sum(record.reconciled_invoice_ids.mapped('amount_total'))

    @api.depends('x_total_facturas', 'x_total_adeudado')
    def _compute_x_total_pagado_facturas(self):
        for record in self:
            record.x_total_pagado_facturas = record.x_total_facturas - record.x_total_adeudado

    @api.depends('reconciled_invoice_ids')
    def _compute_x_vendedores(self):
        for record in self:
            record.x_vendedores = ','.join(record.reconciled_invoice_ids.mapped('invoice_user_id.name'))


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    # MIGRACIÓN V19: en Studio era `related='line_ids.rel_payment'`, pero
    # `line_ids` es `One2many` (puede haber más de un apunte por extracto)
    # y `related=` no soporta atravesar x2many; se reescribe como compute
    # tomando el primer apunte.
    x_pagos_extracto = fields.Many2one(
        'account.payment', string='Pagos extracto', compute='_compute_x_pagos_extracto')

    @api.depends('line_ids.rel_payment')
    def _compute_x_pagos_extracto(self):
        for record in self:
            record.x_pagos_extracto = record.line_ids[:1].rel_payment


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    x_referencia_bancaria = fields.Char(string='Referencia bancaria')
