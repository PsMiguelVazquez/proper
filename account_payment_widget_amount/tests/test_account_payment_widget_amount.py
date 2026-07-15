# -*- coding: utf-8 -*-
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestAccountPaymentWidgetAmount(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.invoice = cls.init_invoice('out_invoice', partner=cls.partner_a, amounts=[1000.0], post=True)
        cls.payment = cls.env['account.payment'].create({
            'amount': 1000.0,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': cls.partner_a.id,
        })
        cls.payment.action_post()
        cls.receivable_line = cls.payment.move_id.line_ids.filtered(
            lambda l: l.account_id.account_type == 'asset_receivable'
        )

    def test_full_assign_without_paid_amount_context(self):
        self.invoice.js_assign_outstanding_line(self.receivable_line.id)
        self.assertEqual(self.invoice.amount_residual, 0.0)
        self.assertTrue(self.invoice.payment_state in ('paid', 'in_payment'))

    def test_partial_assign_caps_amount(self):
        self.invoice.with_context(paid_amount=400.0).js_assign_outstanding_line(self.receivable_line.id)
        self.assertAlmostEqual(self.invoice.amount_residual, 600.0, places=2)
        self.assertEqual(self.invoice.payment_state, 'partial')
        # el resto del pago sigue disponible (no fue consumido de más)
        self.receivable_line.invalidate_recordset()
        self.assertAlmostEqual(self.receivable_line.amount_residual, -600.0, places=2)

    def test_partial_assign_leaves_remaining_payment_usable_elsewhere(self):
        other_invoice = self.init_invoice('out_invoice', partner=self.partner_a, amounts=[400.0], post=True)
        self.invoice.with_context(paid_amount=400.0).js_assign_outstanding_line(self.receivable_line.id)
        other_invoice.js_assign_outstanding_line(self.receivable_line.id)
        self.assertAlmostEqual(self.invoice.amount_residual, 600.0, places=2)
        self.assertEqual(other_invoice.amount_residual, 0.0)
