# -*- coding: utf-8 -*-
from odoo.tests import tagged, TransactionCase
from odoo.exceptions import UserError


@tagged('post_install', '-at_install')
class TestUploadInvoiceWizard(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Cliente upload invoice test'})
        cls.product = cls.env['product.product'].create({
            'name': 'Producto upload invoice test', 'type': 'consu', 'default_code': 'UIW-1',
        })

    def test_upload_invoice_sale_order_creates_wizard(self):
        order = self.env['sale.order'].create({'partner_id': self.partner.id})
        order.order_line = [(0, 0, {'product_id': self.product.id, 'product_uom_qty': 1, 'price_unit': 10.0})]
        order.write({'state': 'sale'})
        action = order.upload_invoice()
        wizard = self.env['upload.invoice.wizard'].browse(action['res_id'])
        self.assertEqual(wizard.tipo, 'sale_order')
        self.assertEqual(wizard.margen, 1.0)

    def test_upload_invoice_sale_order_wrong_state_raises(self):
        order = self.env['sale.order'].create({'partner_id': self.partner.id})
        with self.assertRaises(UserError):
            order.upload_invoice()

    def test_upload_invoice_purchase_order_creates_wizard(self):
        po = self.env['purchase.order'].create({'partner_id': self.partner.id})
        po.write({'state': 'purchase'})
        action = po.upload_invoice()
        wizard = self.env['upload.invoice.wizard'].browse(action['res_id'])
        self.assertEqual(wizard.tipo, 'purchase_order')

    def test_upload_invoice_purchase_order_wrong_state_raises(self):
        po = self.env['purchase.order'].create({'partner_id': self.partner.id})
        with self.assertRaises(UserError):
            po.upload_invoice()

    def test_terminos_pago_id_is_payment_term(self):
        term = self.env['account.payment.term'].search([], limit=1)
        wizard = self.env['upload.invoice.wizard'].create({'terminos_pago_id': term.id})
        self.assertEqual(wizard.terminos_pago_id, term)

    def test_compute_total_ordenes(self):
        order = self.env['sale.order'].create({'partner_id': self.partner.id})
        order.order_line = [(0, 0, {'product_id': self.product.id, 'product_uom_qty': 2, 'price_unit': 50.0})]
        wizard = self.env['upload.invoice.wizard'].create({'sale_ids': [(6, 0, [order.id])]})
        self.assertEqual(wizard.total_ordenes, order.amount_total)

    def test_get_credit_notes_compute(self):
        order = self.env['sale.order'].create({'partner_id': self.partner.id})
        order.order_line = [(0, 0, {'product_id': self.product.id, 'product_uom_qty': 1, 'price_unit': 10.0})]
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice', 'partner_id': self.partner.id, 'sale_id': order.id,
        })
        credit_note = self.env['account.move'].create({
            'move_type': 'out_refund', 'partner_id': self.partner.id, 'reversed_entry_id': invoice.id,
        })
        order.invoice_ids = [(4, invoice.id)]
        self.assertIn(credit_note, order.credit_notes)
