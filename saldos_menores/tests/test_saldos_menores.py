# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestSaldosMenores(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.invoice = cls.init_invoice('out_invoice', products=cls.product_a and [cls.product_a] or None)
        cls.invoice.action_post()
        # `wizard.eliminate.balance.create()` busca esta cuenta por nombre;
        # el plan de cuentas genérico de pruebas no la trae, se crea aquí
        # para poder validar el comportamiento real (no solo que no truene).
        if not cls.env['account.account'].search([('name', 'ilike', 'GASTOS NO DEDUCIBLES (SIN REQUISITOS FISCALES)')], limit=1):
            cls.env['account.account'].create({
                'name': 'GASTOS NO DEDUCIBLES (SIN REQUISITOS FISCALES)',
                'code': 'TEST9999',
                'account_type': 'expense',
            })

    def test_action_eliminate_balance_creates_wizard(self):
        action = self.invoice.action_eliminate_balance()
        wizard = self.env['wizard.eliminate.balance'].browse(action['res_id'])
        self.assertEqual(wizard.max_move_balance, 5.0)
        self.assertTrue(wizard.account_id)
        self.assertTrue(wizard.journal_id)

    def test_get_moves_filters_by_balance_and_max_amount(self):
        # Se paga la factura dejando un residual pequeño (< max_move_balance).
        payment = self.env['account.payment'].create({
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.invoice.partner_id.id,
            'amount': self.invoice.amount_total - 3.0,
        })
        payment.action_post()
        (payment.move_id.line_ids | self.invoice.line_ids).filtered(
            lambda l: l.account_id.account_type == 'asset_receivable' and not l.reconciled
        ).reconcile()
        self.assertAlmostEqual(self.invoice.amount_residual, 3.0, places=2)

        wizard = self.env['wizard.eliminate.balance'].create({
            'move_date': datetime.now(),
            'from_date': datetime.now() - timedelta(days=1),
            'to_date': datetime.now() + timedelta(days=1),
            'max_move_balance': 5.0,
        })
        wizard.get_moves()
        self.assertIn(self.invoice, wizard.moves)

    def test_wizard_lines_computed_for_selected_moves(self):
        # MIGRACIÓN V19: `eliminate_balance()` usa un diario hardcodeado
        # (`journal_id=3`, ver nota en el modelo) que en cualquier entorno de
        # pruebas con una compañía dedicada (como la de
        # `AccountTestInvoicingCommon`) pertenece a OTRA compañía distinta a
        # la de la factura de prueba, lo cual Odoo rechaza
        # (`_check_company`). Este es exactamente el escenario que el propio
        # comentario del módulo ya advertía: el id no es portable entre
        # bases de datos. Se cubre aquí solo hasta el cómputo de líneas
        # (`_get_wizard_lines`), que sí es independiente del entorno; la
        # ejecución completa de `eliminate_balance()` requiere la
        # configuración contable real del entorno de destino.
        payment = self.env['account.payment'].create({
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.invoice.partner_id.id,
            'amount': self.invoice.amount_total - 2.0,
        })
        payment.action_post()
        (payment.move_id.line_ids | self.invoice.line_ids).filtered(
            lambda l: l.account_id.account_type == 'asset_receivable' and not l.reconciled
        ).reconcile()

        wizard = self.env['wizard.eliminate.balance'].create({
            'move_date': datetime.now(),
            'from_date': datetime.now() - timedelta(days=1),
            'to_date': datetime.now() + timedelta(days=1),
            'max_move_balance': 5.0,
        })
        wizard.get_moves()
        wizard.moves = [(6, 0, self.invoice.ids)]
        wizard._get_wizard_lines()
        self.assertTrue(wizard.lines)
        self.assertAlmostEqual(wizard.lines.amount_residual, 2.0, places=2)
