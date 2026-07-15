# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo.tests import tagged, TransactionCase


@tagged('post_install', '-at_install')
class TestConsolidacionCompras(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Consolidacion Compras Test Partner'})
        cls.other_partner = cls.env['res.partner'].create({'name': 'Other Provider'})
        cls.product = cls.env['product.product'].create({
            'name': 'Consolidacion Compras Product', 'type': 'consu', 'default_code': 'CC-1',
        })

    def _create_po(self, partner, qty, price_unit):
        return self.env['purchase.order'].create({
            'partner_id': partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id, 'name': self.product.name,
                'product_qty': qty, 'price_unit': price_unit,
            })],
        })

    def test_view_consolidate_purchase_wizard_creates_wizard_with_merged_lines(self):
        po1 = self._create_po(self.partner, 2, 50.0)
        po2 = self._create_po(self.partner, 3, 50.0)
        action = (po1 | po2).with_context(active_ids=(po1 | po2).ids).view_consolidate_purchase_wizard()
        wizard = self.env['consolidacion.compras.wizard'].browse(action['res_id'])
        self.assertEqual(len(wizard.wizard_lines), 1)
        self.assertEqual(wizard.wizard_lines.product_qty, 5)

    def test_view_consolidate_purchase_wizard_rejects_single_order(self):
        po1 = self._create_po(self.partner, 1, 50.0)
        with self.assertRaises(UserError):
            po1.with_context(active_ids=po1.ids).view_consolidate_purchase_wizard()

    def test_view_consolidate_purchase_wizard_rejects_different_partners(self):
        po1 = self._create_po(self.partner, 1, 50.0)
        po2 = self._create_po(self.other_partner, 1, 50.0)
        with self.assertRaises(UserError):
            (po1 | po2).with_context(active_ids=(po1 | po2).ids).view_consolidate_purchase_wizard()

    def test_done_consolidar_compra_creates_purchase_order_and_marks_consolidated(self):
        po1 = self._create_po(self.partner, 2, 50.0)
        po2 = self._create_po(self.partner, 3, 50.0)
        action = (po1 | po2).with_context(active_ids=(po1 | po2).ids).view_consolidate_purchase_wizard()
        wizard = self.env['consolidacion.compras.wizard'].browse(action['res_id'])
        wizard.done_consolidar_compra()
        self.assertEqual(po1.state, 'consolidate')
        self.assertEqual(po2.state, 'consolidate')
        new_po = self.env['purchase.order'].search([('partner_id', '=', self.partner.id), ('state', '=', 'draft')])
        self.assertEqual(sum(new_po.order_line.mapped('product_qty')), 5)
