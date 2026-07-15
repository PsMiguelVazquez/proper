# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestMrpUnbuildValidate(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.component = cls.env['product.product'].create({
            'name': 'Unbuild Test Component',
            'type': 'consu',
            'is_storable': True,
        })
        cls.kit = cls.env['product.product'].create({
            'name': 'Unbuild Test Kit',
            'type': 'consu',
            'is_storable': True,
        })
        cls.bom = cls.env['mrp.bom'].create({
            'product_tmpl_id': cls.kit.product_tmpl_id.id,
            'product_qty': 1.0,
            'type': 'normal',
            'bom_line_ids': [(0, 0, {'product_id': cls.component.id, 'product_qty': 1.0})],
        })
        cls.warehouse = cls.env['stock.warehouse'].search([('company_id', '=', cls.env.company.id)], limit=1)
        cls.stock_loc = cls.warehouse.lot_stock_id

    def test_action_validate_raises_without_enough_stock(self):
        unbuild = self.env['mrp.unbuild'].create({
            'product_id': self.kit.id,
            'bom_id': self.bom.id,
            'product_qty': 5.0,
            'product_uom_id': self.kit.uom_id.id,
            'location_id': self.stock_loc.id,
            'location_dest_id': self.stock_loc.id,
        })
        with self.assertRaises(UserError):
            unbuild.action_validate()

    def test_action_validate_succeeds_with_enough_stock(self):
        self.env['stock.quant']._update_available_quantity(self.kit, self.stock_loc, 5.0)
        unbuild = self.env['mrp.unbuild'].create({
            'product_id': self.kit.id,
            'bom_id': self.bom.id,
            'product_qty': 5.0,
            'product_uom_id': self.kit.uom_id.id,
            'location_id': self.stock_loc.id,
            'location_dest_id': self.stock_loc.id,
        })
        unbuild.action_validate()
        self.assertEqual(unbuild.state, 'done')
