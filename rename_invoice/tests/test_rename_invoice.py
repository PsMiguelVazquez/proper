# -*- coding: utf-8 -*-
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestRenameInvoice(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.invoice = cls.init_invoice('out_invoice', products=cls.product_a and [cls.product_a] or None)
        cls.invoice.action_post()

    def test_cfdi_filename_matches_invoice_name(self):
        expected = self.invoice.name.replace('/', '') + '.xml'
        self.assertEqual(self.invoice._l10n_mx_edi_get_invoice_cfdi_filename(), expected)
