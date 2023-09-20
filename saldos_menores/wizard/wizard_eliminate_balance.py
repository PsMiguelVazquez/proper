# -*- coding: utf-8 -*-
from collections import defaultdict
from datetime import datetime

from odoo import models, fields, _, api
from odoo.exceptions import UserError, ValidationError
from lxml.objectify import fromstring
class WizardEliminateBalance(models.TransientModel):
    _name = 'wizard.eliminate.balance'

    move_date = fields.Date(string='Fecha del movimiento')
    from_date = fields.Date(string='Desde')
    to_date = fields.Date(string='Hasta')
    partner_id = fields.Many2one('res.partner', string='Cliente')
    max_move_balance = fields.Float('Saldo menor a')
    moves = fields.Many2many('account.move', string='Movimientos')
    lines = fields.Many2many('wizard.eliminate.line', compute='_get_wizard_lines')

    @api.depends('moves')
    def _get_wizard_lines(self):
        for record in self:
            record.lines = self.env['wizard.eliminate.line']
            lines_list = []
            for move in record.moves:
                origin_move = self.env['account.move'].browse(move.id.origin)
                lines_list.append({
                    'invoice_name':origin_move.name,
                    'partner_id':origin_move.partner_id.id,
                    'amount_total':origin_move.amount_total_signed,
                    'amount_payed': origin_move.amount_total_signed - origin_move.amount_residual,
                    'amount_residual':origin_move.amount_residual,
                    'wizard_id': self.ids[0],
                    'move_id': origin_move.id,
                })
            if lines_list:
                lines = self.env['wizard.eliminate.line'].create(lines_list)
            else:
                lines = None
            record.lines = lines

    @api.onchange('from_date','to_date', 'max_move_balance','partner_id')
    def get_moves(self):
        for record in self:
            if record.partner_id:
                record.moves = self.env['account.move'].search([
                    ('create_date', '>=',  record.from_date),
                    ('create_date', '<=',  record.to_date),
                    ('amount_residual','<',record.max_move_balance),
                    ('amount_residual','>', 0.1),
                    ('state','=', 'posted'),
                    ('partner_id', '=', record.partner_id.id)
                ])
            else:
                record.moves = self.env['account.move'].search([
                    ('create_date', '>=', record.from_date),
                    ('create_date', '<=', record.to_date),
                    ('amount_residual', '<', record.max_move_balance),
                    ('amount_residual', '>', 0.1),
                    ('state', '=', 'posted')
                ])
            print(record.moves)

    def eliminate_balance(self):
        move_lines_d = []
        lineas = self.env['wizard.eliminate.line'].search([('wizard_id', '=', self.id)])
        if lineas:
            for inv in lineas:
                move_line_vals = {
                    'debit': inv.amount_residual,
                    "partner_id": inv.partner_id.id,
                    "name": 'Eliminación de saldos menores',
                    "account_id": inv.partner_id.property_account_receivable_id.id,
                }
                move_lines_d.append((0, 0, move_line_vals))
            move_line_vals = {
                'credit': sum(lineas.mapped('amount_residual')),
                "partner_id": inv.partner_id.id,
                "name": 'Eliminación de saldos menores',
                "account_id": inv.partner_id.property_account_receivable_id.id,
            }
            move_lines_d.append((0, 0, move_line_vals))
        move = self.env['account.move'].create({
            'ref': _(', '.join(lineas.mapped(('invoice_name'))))
            , 'journal_id': 3
        })
        move.write({"line_ids": move_lines_d})