# -*- coding: utf-8 -*-
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestAccountPaymentRegisterProper(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.invoice = cls.init_invoice('out_invoice', products=cls.product_a and [cls.product_a] or None)
        cls.invoice.action_post()

    def test_action_create_payments_attaches_receipt(self):
        wizard = self.env['account.payment.register'].with_context(
            active_model='account.move', active_ids=self.invoice.ids
        ).create({})
        wizard.action_create_payments()

        self.assertTrue(wizard.registered_payment_id)
        payment = wizard.registered_payment_id
        attachment = self.env['ir.attachment'].search([
            ('res_model', '=', 'account.move'),
            ('res_id', '=', payment.move_id.id),
            ('name', '=', 'Complemento de pago.pdf'),
        ])
        self.assertTrue(attachment, "El comprobante de pago debe adjuntarse al asiento del pago")
        self.assertEqual(attachment.mimetype, 'application/pdf')

    def test_partner_bank_ref_domain_onchange(self):
        wizard = self.env['account.payment.register'].with_context(
            active_model='account.move', active_ids=self.invoice.ids
        ).create({})
        result = wizard.deoman_banks()
        self.assertIn('domain', result)
        self.assertIn('partner_bank_ref', result['domain'])
