# -*- coding: utf-8 -*-
from odoo.tests import tagged, TransactionCase


@tagged('post_install', '-at_install')
class TestBlockEditSaleOrder(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # `sale_purchase_confirm` exige nivel de cliente, documento/método de
        # entrega y al menos una línea con producto de tipo `service` (para
        # no depender de existencias) antes de poder confirmar una orden.
        nivel = cls.env['x_niveles_de_cliente'].create({'x_name': 'A'})
        cls.partner = cls.env['res.partner'].create({'name': 'Block Edit Test Partner', 'x_nivel_cliente': nivel.id})
        cls.product = cls.env['product.product'].create({
            'name': 'Block Edit Test Product', 'type': 'service', 'default_code': 'BES-1',
        })
        cls.order = cls.env['sale.order'].create({
            'partner_id': cls.partner.id,
            'x_doc_entrega': 'factura',
            'x_metodo_entrega': 'flotilla',
            'order_line': [(0, 0, {'product_id': cls.product.id, 'product_uom_qty': 1, 'price_unit': 10.0})],
        })

    def test_edit_blocked_false_while_draft(self):
        self.assertFalse(self.order.edit_blocked)

    def test_edit_blocked_true_after_confirm(self):
        self.order.action_confirm()
        self.assertTrue(self.order.edit_blocked)

    def test_request_and_approve_invoicing(self):
        self.order.request_approve_invoicing()
        self.assertTrue(self.order.approve_invoicing_requested)
        initial = self.order.invoice_approved
        self.order.approve_invoicing()
        self.assertEqual(self.order.invoice_approved, not initial)
        self.assertFalse(self.order.approve_invoicing_requested)

    def test_get_credit_notes_empty_without_refunds(self):
        self.assertFalse(self.order.credit_notes)
