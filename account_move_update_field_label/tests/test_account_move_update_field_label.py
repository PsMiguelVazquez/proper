# -*- coding: utf-8 -*-
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestAccountMoveUpdateFieldLabel(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.invoice = cls.init_invoice('out_invoice', products=cls.product_a and [cls.product_a] or None)

    def test_action_post_sets_usuario_timbrado(self):
        self.invoice.action_post()
        self.assertEqual(self.invoice.usuario_timbrado, self.env.user)

    def test_button_draft_clears_fields(self):
        self.invoice.action_post()
        self.invoice.version_cfdi = 'some-technical-value'
        self.invoice.button_draft()
        self.assertFalse(self.invoice.usuario_timbrado)
        self.assertFalse(self.invoice.version_cfdi)

    def test_codigo_uso_cfdi_compute(self):
        self.invoice.l10n_mx_edi_usage = 'G01'
        self.assertEqual(self.invoice.codigo_uso_cfdi, 'G01')
        self.invoice.l10n_mx_edi_usage = False
        self.assertEqual(self.invoice.codigo_uso_cfdi, '')
