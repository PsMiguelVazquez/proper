# -*- coding: utf-8 -*-
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.exceptions import ValidationError
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestEndosoProper(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_partner = cls.env['res.partner'].create({
            'name': 'Endoso Target Partner',
            'property_account_receivable_id': cls.partner_a.property_account_receivable_id.id,
        })
        cls.invoice = cls.init_invoice('out_invoice', products=cls.product_a and [cls.product_a] or None)
        cls.invoice.action_post()
        cls.env['account.journal'].create({
            'name': 'Endoso',
            'code': 'ENDOSO',
            'type': 'general',
        })

    def test_endosar_factura_creates_wizard(self):
        action = self.invoice.endosar_factura()
        wizard = self.env['endoso.wizard'].browse(action['res_id'])
        self.assertEqual(wizard.factura, self.invoice)

    def test_done_endoso_requires_cfdi_uuid(self):
        wizard = self.env['endoso.wizard'].create({
            'factura': self.invoice.id,
            'cliente': self.other_partner.id,
            'porcentaje': 1,
        })
        with self.assertRaises(ValidationError):
            wizard.done_endoso()

    def test_done_endoso_rejects_same_partner(self):
        wizard = self.env['endoso.wizard'].create({
            'factura': self.invoice.id,
            'cliente': self.invoice.partner_id.id,
            'porcentaje': 1,
        })
        with self.assertRaises(ValidationError):
            wizard.done_endoso()

    def test_done_endoso_creates_and_posts_endoso_move(self):
        self.invoice.l10n_mx_edi_cfdi_uuid = 'TEST-UUID-1234'
        wizard = self.env['endoso.wizard'].create({
            'factura': self.invoice.id,
            'cliente': self.other_partner.id,
            'porcentaje': 1,
        })
        action = wizard.done_endoso()
        endoso = self.env['endoso.move'].browse(action['res_id'])
        self.assertEqual(endoso.state, 'posted')
        self.assertEqual(endoso.origin_invoice, self.invoice)
        self.assertEqual(endoso.partner_id, self.other_partner)
        self.assertTrue(self.invoice.ocultar_endoso)
