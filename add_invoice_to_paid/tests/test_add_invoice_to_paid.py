# -*- coding: utf-8 -*-
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.exceptions import UserError
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestAddInvoiceToPaid(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.invoice = cls.init_invoice('out_invoice', products=cls.product_a and [cls.product_a] or None)
        cls.invoice.action_post()
        cls.payment = cls.env['account.payment'].create({
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': cls.invoice.partner_id.id,
            'amount': cls.invoice.amount_total,
        })
        cls.payment.action_post()

    def test_amount_rest_defaults_to_full_amount_when_unreconciled(self):
        self.assertEqual(self.payment.amount_rest, self.payment.amount)

    def test_asign_invoices_creates_wizard(self):
        action = self.payment.asign_invoices()
        wizard = self.env['account.payment.wizard.ex'].browse(action['res_id'])
        self.assertEqual(wizard.payment, self.payment)
        self.assertEqual(wizard.partner_id, self.payment.partner_id)

    def test_amount_applied_sums_porcent_assign(self):
        self.invoice.porcent_assign = 30.0
        wizard = self.env['account.payment.wizard.ex'].create({
            'payment': self.payment.id,
            'partner_id': self.payment.partner_id.id,
            'invoices_ids': [(6, 0, self.invoice.ids)],
        })
        self.assertEqual(wizard.amount_applied, 30.0)

    def test_done_rejects_amount_over_available(self):
        self.invoice.porcent_assign = self.payment.amount_rest + 1000.0
        wizard = self.env['account.payment.wizard.ex'].create({
            'payment': self.payment.id,
            'partner_id': self.payment.partner_id.id,
            'invoices_ids': [(6, 0, self.invoice.ids)],
        })
        with self.assertRaises(UserError):
            wizard.done()
