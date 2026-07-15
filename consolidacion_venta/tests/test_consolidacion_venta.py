# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo.tests import tagged, TransactionCase


@tagged('post_install', '-at_install')
class TestConsolidacionVenta(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # `sale_purchase_confirm` exige un nivel de cliente (para calcular
        # márgenes) y documento/método de entrega antes de poder confirmar
        # una orden de venta; se configuran aquí para no romper estos tests.
        nivel = cls.env['x_niveles_de_cliente'].create({'x_name': 'A'})
        cls.partner = cls.env['res.partner'].create({'name': 'Consolidacion Test Partner', 'x_nivel_cliente': nivel.id})
        cls.other_partner = cls.env['res.partner'].create({'name': 'Other Partner', 'x_nivel_cliente': nivel.id})
        # `type='service'` evita la validación de existencias de
        # `sale_purchase_confirm.is_valid_order_sale` (no aplica a servicios).
        cls.product = cls.env['product.product'].create({
            'name': 'Consolidacion Product',
            'type': 'service',
            'default_code': 'CONS-TEST-1',
            'invoice_policy': 'order',
        })

    def _create_confirmed_order(self, partner, qty, price_unit):
        order = self.env['sale.order'].create({
            'partner_id': partner.id,
            'x_doc_entrega': 'factura',
            'x_metodo_entrega': 'flotilla',
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': qty,
                'price_unit': price_unit,
            })],
        })
        order.action_confirm()
        return order

    def test_view_consolidate_lines_wizard_creates_wizard_with_consolidated_lines(self):
        order1 = self._create_confirmed_order(self.partner, 2, 100.0)
        order2 = self._create_confirmed_order(self.partner, 3, 100.0)
        action = (order1 | order2).with_context(active_ids=(order1 | order2).ids).view_consolidate_lines_wizard()
        wizard = self.env['consolidacion.wizard'].browse(action['res_id'])
        self.assertEqual(len(wizard.lines), 1)
        self.assertEqual(wizard.lines.quantity, 5)

    def test_view_consolidate_lines_wizard_rejects_different_partners(self):
        order1 = self._create_confirmed_order(self.partner, 1, 100.0)
        order2 = self._create_confirmed_order(self.other_partner, 1, 100.0)
        with self.assertRaises(UserError):
            (order1 | order2).with_context(active_ids=(order1 | order2).ids).view_consolidate_lines_wizard()

    def test_done_consolidar_creates_invoice_and_marks_orders_invoiced(self):
        order1 = self._create_confirmed_order(self.partner, 2, 100.0)
        order2 = self._create_confirmed_order(self.partner, 3, 100.0)
        action = (order1 | order2).with_context(active_ids=(order1 | order2).ids).view_consolidate_lines_wizard()
        wizard = self.env['consolidacion.wizard'].browse(action['res_id'])
        result = wizard.done_consolidar()
        invoice = self.env['account.move'].browse(result['res_id'])
        self.assertEqual(invoice.move_type, 'out_invoice')
        self.assertEqual(sum(invoice.invoice_line_ids.mapped('quantity')), 5)
        self.assertEqual(order1.invoice_status, 'invoiced')
        self.assertEqual(order2.invoice_status, 'invoiced')
        self.assertIn(invoice, order1.invoice_ids)
        self.assertIn(invoice, order2.invoice_ids)
