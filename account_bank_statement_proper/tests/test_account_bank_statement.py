# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestAccountBankStatementProper(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.bank_journal = cls.company_data['default_journal_bank']
        cls.cash_journal = cls.company_data['default_journal_cash']
        cls.payment = cls.env['account.payment'].create({
            'amount': 100.0,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': cls.partner_a.id,
            'journal_id': cls.bank_journal.id,
        })
        cls.payment.action_post()

    def _create_statement(self, journal, rel_payment=False):
        return self.env['account.bank.statement'].create({
            'journal_id': journal.id,
            'balance_start': 0.0,
            'balance_end_real': rel_payment.amount if rel_payment else 0.0,
            'line_ids': [(0, 0, {
                'journal_id': journal.id,
                'payment_ref': 'test line',
                'amount': rel_payment.amount if rel_payment else 0.0,
                'rel_payment': rel_payment.id if rel_payment else False,
            })],
        })

    def test_matching_journal_is_accepted(self):
        statement = self._create_statement(self.bank_journal, self.payment)
        self.assertEqual(statement.line_ids.rel_payment, self.payment)

    def test_mismatched_journal_raises(self):
        with self.assertRaises(UserError):
            self._create_statement(self.cash_journal, self.payment)

    def test_duplicate_payment_across_statements_raises(self):
        self._create_statement(self.bank_journal, self.payment)
        with self.assertRaises(UserError):
            self._create_statement(self.bank_journal, self.payment)

    def test_duplicate_payment_same_statement_raises(self):
        with self.assertRaises(ValidationError):
            self.env['account.bank.statement'].create({
                'journal_id': self.bank_journal.id,
                'balance_start': 0.0,
                'line_ids': [
                    (0, 0, {
                        'journal_id': self.bank_journal.id,
                        'payment_ref': 'line 1',
                        'amount': 50.0,
                        'rel_payment': self.payment.id,
                    }),
                    (0, 0, {
                        'journal_id': self.bank_journal.id,
                        'payment_ref': 'line 2',
                        'amount': 50.0,
                        'rel_payment': self.payment.id,
                    }),
                ],
            })

    def test_onchange_payment_id_fills_line(self):
        line = self.env['account.bank.statement.line'].new({
            'journal_id': self.bank_journal.id,
        })
        line.rel_payment = self.payment
        line.on_change_payment_id()
        self.assertEqual(line.amount, self.payment.amount)
        self.assertEqual(line.partner_id, self.payment.partner_id)
