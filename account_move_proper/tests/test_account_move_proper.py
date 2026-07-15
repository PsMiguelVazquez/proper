# -*- coding: utf-8 -*-
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.exceptions import UserError
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestAccountMoveProper(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.invoice = cls.init_invoice('out_invoice', products=cls.product_a and [cls.product_a] or None)

    def test_remision_name_draft_out_invoice(self):
        self.assertEqual(self.invoice.remision_name, str(self.invoice.id))

    def test_remision_name_empty_for_other_move_types(self):
        bill = self.init_invoice('in_invoice', products=self.product_a and [self.product_a] or None)
        self.assertEqual(bill.remision_name, '')

    def test_cantidad_facturada_total(self):
        expected = sum(self.invoice.invoice_line_ids.mapped('quantity'))
        self.assertEqual(self.invoice.cantidad_facturada_total, expected)

    def test_compute_orden_compra_without_sale_order(self):
        self.assertEqual(self.invoice.x_studio_n_orden_de_compra, '')

    def test_compute_orden_compra_from_sale_order(self):
        # `sudo()`: el usuario de prueba de `AccountTestInvoicingCommon` no
        # pertenece al grupo de Ventas y no puede crear `sale.order`
        # directamente; no es lo que este test valida.
        order = self.env['sale.order'].sudo().create({
            'partner_id': self.invoice.partner_id.id,
            'x_studio_n_orden_de_compra': 'PO-1234',
        })
        self.invoice.sale_id = order
        self.assertEqual(self.invoice.x_studio_n_orden_de_compra, 'PO-1234')

    def test_ejecutivo_cuenta_related_to_partner(self):
        agent = self.env['res.users'].search([], limit=1)
        agent.x_studio_clave_del_vendedor_1 = 'AG01'
        self.invoice.partner_id.sales_agent = agent
        self.assertEqual(self.invoice.ejecutivo_cuenta, 'AG01')

    def test_duplicate_invoice_requires_posted_state(self):
        with self.assertRaises(UserError):
            self.invoice.with_context(active_id=self.invoice.id).duplicate_invoice()

    def test_duplicate_invoice_requires_cfdi_uuid(self):
        self.invoice.action_post()
        with self.assertRaises(UserError):
            self.invoice.with_context(active_id=self.invoice.id).duplicate_invoice()

    def test_mark_as_cancelled_requires_valid_motivo(self):
        with self.assertRaises(UserError):
            self.invoice.with_context(active_ids=self.invoice.ids).mark_as_cancelled()

    def test_mark_as_cancelled_rejects_motivo_01(self):
        self.invoice.motivo_cancelacion = '01'
        with self.assertRaises(UserError):
            self.invoice.with_context(active_ids=self.invoice.ids).mark_as_cancelled()
