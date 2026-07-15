# -*- coding: utf-8 -*-
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.exceptions import UserError
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestNeteoProper(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.invoice = cls.init_invoice('out_invoice', products=cls.product_a and [cls.product_a] or None)
        cls.invoice.action_post()
        cls.bill = cls.init_invoice('in_invoice', products=cls.product_a and [cls.product_a] or None)
        cls.bill.action_post()
        cls.bill.porcent_assign = cls.bill.amount_total

    def test_compensar_factura_creates_wizard(self):
        action = self.invoice.compensar_factura()
        wizard = self.env['neteo.wizard'].browse(action['res_id'])
        self.assertEqual(wizard.factura_cliente, self.invoice)
        self.assertEqual(wizard.cliente, self.invoice.partner_id)
        self.assertEqual(wizard.amount_cliente, self.invoice.amount_residual)

    def test_done_neteo_requires_journal(self):
        wizard = self.env['neteo.wizard'].create({
            'factura_cliente': self.invoice.id,
            'cliente': self.invoice.partner_id.id,
            'facturas_proveedor': [(6, 0, self.bill.ids)],
        })
        with self.assertRaises(UserError):
            wizard.done_neteo()

    def test_done_neteo_creates_and_posts_neteo_move(self):
        self.env['account.journal'].create({
            'name': 'Neteo',
            'code': 'NETEO',
            'type': 'general',
        })
        wizard = self.env['neteo.wizard'].create({
            'factura_cliente': self.invoice.id,
            'cliente': self.invoice.partner_id.id,
            'facturas_proveedor': [(6, 0, self.bill.ids)],
        })
        self.assertEqual(wizard.amount, self.bill.porcent_assign)
        action = wizard.done_neteo()
        neteo = self.env['neteo.move'].browse(action['res_id'])
        self.assertEqual(neteo.state, 'posted')
        self.assertEqual(len(neteo.line_ids), 2)
        self.assertEqual(sum(neteo.line_ids.mapped('debit')), wizard.amount)
        self.assertEqual(sum(neteo.line_ids.mapped('credit')), wizard.amount)
