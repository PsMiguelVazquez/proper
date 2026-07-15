# -*- coding: utf-8 -*-
from odoo.tests import tagged, TransactionCase


@tagged('post_install', '-at_install')
class TestSaleOrderUtilities(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        nivel = cls.env['x_niveles_de_cliente'].create({'x_name': 'A'})
        cls.partner = cls.env['res.partner'].create({'name': 'Sale Order Utilities Test Partner', 'x_nivel_cliente': nivel.id})
        cls.product = cls.env['product.product'].create({
            'name': 'Sale Order Utilities Test Product', 'type': 'service', 'default_code': 'SOU-1',
        })
        cls.order = cls.env['sale.order'].create({
            'partner_id': cls.partner.id,
            'x_doc_entrega': 'factura',
            'x_metodo_entrega': 'flotilla',
            'order_line': [(0, 0, {'product_id': cls.product.id, 'product_uom_qty': 1, 'price_unit': 10.0})],
        })

    def test_edit_blocked_true_after_confirm(self):
        self.assertFalse(self.order.edit_blocked)
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

    def test_cantidad_por_comprar_zero_when_not_partial(self):
        line = self.order.order_line[0]
        self.assertEqual(line.cantidad_por_comprar, 0.0)

    def test_product_template_x_studio_rama_field(self):
        self.product.product_tmpl_id.x_studio_rama = 'LINEA'
        self.assertEqual(self.product.product_tmpl_id.x_studio_rama, 'LINEA')


@tagged('post_install', '-at_install')
class TestDataValidate(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        nivel = cls.env['x_niveles_de_cliente'].create({'x_name': 'A'})
        cls.partner = cls.env['res.partner'].create({'name': 'Data Validate Test Partner', 'x_nivel_cliente': nivel.id})
        cls.product = cls.env['product.product'].create({
            'name': 'Data Validate Test Product', 'type': 'service', 'default_code': 'DV-1',
        })
        cls.order = cls.env['sale.order'].create({
            'partner_id': cls.partner.id,
            'x_doc_entrega': 'factura',
            'x_metodo_entrega': 'flotilla',
            'order_line': [(0, 0, {
                'product_id': cls.product.id, 'product_uom_qty': 1, 'price_unit': 10.0,
                'x_validacion_precio': True, 'x_cantidad_disponible_compra': 5,
                'x_studio_nuevo_costo': 20.0, 'x_tiempo_entrega_compra': '3 días',
            })],
        })
        cls.line = cls.order.order_line[0]

    def test_migrate_lines_creates_data_validate(self):
        self.env['data.validate'].migrate_lines()
        record = self.env['data.validate'].search([('order_line_id', '=', self.line.id)])
        self.assertTrue(record)
        self.assertEqual(record.product_qty_purchases, 5)
        self.assertEqual(record.new_cost, 20.0)
        self.assertEqual(record.delivery_time, '3 días')

    def test_migrate_lines_does_not_duplicate(self):
        self.env['data.validate'].migrate_lines()
        self.env['data.validate'].migrate_lines()
        records = self.env['data.validate'].search([('order_line_id', '=', self.line.id)])
        self.assertEqual(len(records), 1)

    def test_branch_related_to_product_template(self):
        self.product.product_tmpl_id.x_studio_rama = 'CATALOGO'
        record = self.env['data.validate'].create({'order_line_id': self.line.id})
        self.assertEqual(record.branch, 'CATALOGO')

    def test_on_change_new_cost_writes_to_order_line(self):
        record = self.env['data.validate'].new({'order_line_id': self.line.id})
        record.new_cost = 99.0
        record.on_change_new_cost()
        self.assertEqual(record.order_line_id.x_studio_nuevo_costo, 99.0)
