# -*- coding: utf-8 -*-
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.exceptions import UserError
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestFactorajeFinanciero(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_partner = cls.env['res.partner'].create({'name': 'Other Partner'})
        cls.invoice = cls.init_invoice('out_invoice', products=cls.product_a and [cls.product_a] or None)
        cls.invoice.action_post()

    def test_balance_after_factoring_compute(self):
        self.invoice.factoring_amount = 10.0
        self.invoice.porcent_assign = 5.0
        expected = self.invoice.amount_residual - 10.0 - 5.0
        self.assertEqual(self.invoice.balance_after_factoring, expected)

    def test_balance_after_compensate_compute(self):
        self.invoice.porcent_assign = 5.0
        expected = self.invoice.amount_residual - 5.0
        self.assertEqual(self.invoice.balance_after_compensate, expected)

    def test_on_balance_after_factoring_onchange_fills_porcent_assign(self):
        self.invoice.porcent_assign = 0.0
        self.invoice.factoring_amount = 25.0
        # `balance_after_factoring` depende de `porcent_assign`, así que se
        # captura su valor ANTES de la asignación (después de asignar,
        # `balance_after_factoring` se recalcula con el nuevo porcent_assign
        # y da 0, ya que ese es justo el punto del método: dejar el saldo en 0).
        expected = self.invoice.balance_after_factoring
        self.invoice.on_balance_after_factoring()
        self.assertEqual(self.invoice.porcent_assign, expected)
        self.assertEqual(self.invoice.balance_after_factoring, 0.0)

    def test_view_compensate_wizard_rejects_different_partners(self):
        other_invoice = self.init_invoice('out_invoice', partner=self.other_partner, products=self.product_a and [self.product_a] or None)
        other_invoice.action_post()
        with self.assertRaises(UserError):
            (self.invoice | other_invoice).with_context(
                active_ids=(self.invoice | other_invoice).ids
            ).view_compensate_wizard()

    def test_view_financial_factoring_wizard_rejects_different_partners(self):
        other_invoice = self.init_invoice('out_invoice', partner=self.other_partner, products=self.product_a and [self.product_a] or None)
        other_invoice.action_post()
        with self.assertRaises(UserError):
            (self.invoice | other_invoice).with_context(
                active_ids=(self.invoice | other_invoice).ids
            ).view_financial_factoring_wizard()

    def test_payment_endosos_count_defaults_to_zero(self):
        payment = self.env['account.payment'].create({
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.invoice.partner_id.id,
            'amount': 50.0,
        })
        self.assertEqual(payment.endosos_count, 0)
