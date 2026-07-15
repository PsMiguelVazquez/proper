# -*- coding: utf-8 -*-
from collections import defaultdict
from datetime import datetime

from odoo import models, fields, _, api
from odoo.exceptions import UserError, ValidationError


class WizardEliminateBalance(models.TransientModel):
    _name = 'wizard.eliminate.balance'
    _description = 'Eliminación de saldos menores'

    move_date = fields.Date(string='Fecha del movimiento')
    from_date = fields.Date(string='Desde')
    to_date = fields.Date(string='Hasta')
    partner_id = fields.Many2one('res.partner', string='Cliente')
    max_move_balance = fields.Float('Saldo menor a')
    moves = fields.Many2many('account.move', string='Movimientos')
    payments = fields.Many2many('account.payment', string='Pagos')
    lines = fields.Many2many('wizard.eliminate.line', compute='_get_wizard_lines')
    account_id = fields.Many2one('account.account')
    # MIGRACIÓN V19: `journal_id=3` es un id interno hardcodeado de la base de
    # producción de 15.0 (diario específico para el asiento de eliminación de
    # saldos). No es portable entre bases de datos; debe verificarse/ajustarse
    # contra la configuración contable real del entorno de destino.
    journal_id = fields.Many2one('account.journal')

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        account = self.env['account.account'].search([('name', 'ilike', 'GASTOS NO DEDUCIBLES (SIN REQUISITOS FISCALES)')], limit=1)
        journal = self.env['account.journal'].browse(3)
        records.account_id = account.id
        records.journal_id = journal.id
        return records

    @api.depends('moves')
    def _get_wizard_lines(self):
        for record in self:
            record.lines = self.env['wizard.eliminate.line']
            lines_list = []
            for move in record.moves:
                # MIGRACIÓN V19: en 15.0 este código hacía
                # `self.env['account.move'].browse(move.id.origin)`, lo cual
                # nunca pudo haber funcionado (`move.id` es un entero, no
                # tiene atributo `.origin`) - código muerto desde su origen.
                # El movimiento sobre el que se calculan estos datos es el
                # propio `move`.
                origin_move = move
                lines_list.append({
                    'invoice_name':origin_move.name,
                    'invoice_id': origin_move.id,
                    'partner_id':origin_move.partner_id.id,
                    'amount_total':origin_move.amount_total_signed,
                    'amount_payed': origin_move.amount_total_signed - origin_move.amount_residual,
                    'amount_residual':origin_move.amount_residual_signed,
                    'wizard_id': self.ids[0],
                    'move_id': origin_move.id,
                    'type': 'Factura'
                })
            for payment in record.payments:
                # MIGRACIÓN V19: mismo caso que arriba
                # (`payment.move_id.id.origin` nunca funcionó).
                origin_move = payment.move_id
                lines_list.append({
                    'invoice_name': origin_move.name,
                    'invoice_id': origin_move.id,
                    'partner_id': origin_move.partner_id.id,
                    'amount_total': origin_move.amount_total_signed,
                    'amount_payed': origin_move.amount_total_signed - origin_move.amount_residual,
                    'amount_residual': -payment.amount_rest,
                    'wizard_id': self.ids[0],
                    'move_id': origin_move.id,
                    'type': 'Pago'
                })
            if lines_list:
                lines = self.env['wizard.eliminate.line'].create(lines_list)
            else:
                lines = None
            record.lines = lines

    @api.onchange('from_date','to_date', 'max_move_balance','partner_id')
    def get_moves(self):
        for record in self:
            record.moves = self.env['account.move'].search([
                ('create_date', '>=', record.from_date),
                ('create_date', '<=', record.to_date),
                ('amount_residual', '<=', record.max_move_balance),
                ('amount_residual', '>=', -record.max_move_balance),
                ('amount_residual', '!=', 0.0),
                ('state', '=', 'posted')
            ])
            pays = self.env['account.payment'].search([
                ('date', '>=', record.from_date),
                ('date', '<=', record.to_date),
                ('state', '=', 'posted')
            ])
            record.payments = pays.filtered(lambda x: x.amount_rest >= -record.max_move_balance and x.amount_rest <= record.max_move_balance and round(x.amount_rest, 2) != 0.0)

    def eliminate_balance(self):
        move_lines_d = []
        lineas = self.env['wizard.eliminate.line'].search([('wizard_id', '=', self.id)])
        if lineas:
            suma = sum(lineas.mapped('amount_residual'))
            if suma < 0:
                move_lines_d.append((0, 0, {
                    'credit': -suma,
                    "name": 'Eliminación de saldos menores',
                    "account_id": self.account_id.id,
                }))
            else:
                move_lines_d.append((0, 0, {
                    'debit': suma,
                    "name": 'Eliminación de saldos menores',
                    "account_id": self.account_id.id,
                }))
            for inv in lineas:
                '''
                    Crea un abono al cliente por la saldo de la cada factura
                '''
                if inv.amount_residual < 0:
                    move_line_vals = {
                        'debit': -inv.amount_residual,
                        "partner_id": inv.partner_id.id,
                        "name": 'Eliminación de saldos menores',
                        "account_id": inv.partner_id.property_account_receivable_id.id,
                    }
                else:
                    move_line_vals = {
                        'credit': inv.amount_residual,
                        "partner_id": inv.partner_id.id,
                        "name": 'Eliminación de saldos menores',
                        "account_id": inv.partner_id.property_account_receivable_id.id,
                    }
                move_lines_d.append((0, 0, move_line_vals))
            '''
                Crea el apunte con el total de saldos menores con un cargo en la cuenta Gastos no deducibles
            '''
        move = self.env['account.move'].create({
            'ref': _(', '.join(lineas.mapped(('invoice_name'))))
            , 'journal_id': self.journal_id.id
            , 'date': self.move_date
        })
        move.write({"line_ids": move_lines_d})
        move.action_post()
        invoices_to_reconcile = lineas.invoice_id
        for line in move.line_ids:
            inv_to_rec = invoices_to_reconcile.filtered(lambda x: x.amount_residual == line.credit)
            line_to_rec = inv_to_rec.line_ids.filtered(lambda y: y.account_id == line.account_id and not y.reconciled)
            if line_to_rec:
                to_reconcile = line + line_to_rec[0]
                to_reconcile.with_context({'no_exchange_difference': True}).reconcile()
        invoice_msg = (
                          "Se realizó el proceso de eliminación de saldos desde: <a href=# data-oe-model=account.move data-oe-id=%d>%s</a>") % (
                          move.id, move.name)
        for inv in invoices_to_reconcile:
            # MIGRACIÓN V19: `message_post(..., type=...)` -> el parámetro se
            # llama `message_type` (además, todos los parámetros de
            # `message_post` son ahora solo por keyword).
            inv.message_post(body=invoice_msg, message_type="notification")

        msg = (
                "Se realizó eliminación de saldos: " +
                ", ".join([("<a href=# data-oe-model=account.move data-oe-id=%d>%s</a>") % (x.id, x.name)
                           for x in invoices_to_reconcile]))
        move.message_post(body=msg, message_type="notification")
        result = {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "domain": [('id', 'in', invoices_to_reconcile.ids)],
            "context": {"create": False, 'default_move_type': 'out_invoice'},
            "name": _("Customer Invoices"),
            'view_mode': 'list,form',
        }
        return result
