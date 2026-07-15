# -*- coding: utf-8 -*-
from odoo.tests import tagged, TransactionCase


@tagged('post_install', '-at_install')
class TestCostoPromedioProper(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Costo Promedio Test Partner'})
        cls.purchase = cls.env['purchase.order'].create({'partner_id': cls.partner.id})
        cls.picking_type_in = cls.env.ref('stock.picking_type_in')
        cls.picking = cls.env['stock.picking'].create({
            'partner_id': cls.partner.id,
            'picking_type_id': cls.picking_type_in.id,
            'location_id': cls.picking_type_in.default_location_src_id.id,
            'location_dest_id': cls.picking_type_in.default_location_dest_id.id,
            'origin': cls.purchase.name,
        })

    def test_compute_origin_matches_purchase_order(self):
        self.assertEqual(self.picking.related_purchase_id, self.purchase)
        self.assertEqual(self.picking.related_sale_id, self.purchase.sale_ids)

    def test_compute_origin_no_match(self):
        picking = self.env['stock.picking'].create({
            'partner_id': self.partner.id,
            'picking_type_id': self.picking_type_in.id,
            'location_id': self.picking_type_in.default_location_src_id.id,
            'location_dest_id': self.picking_type_in.default_location_dest_id.id,
            'origin': 'NO-SUCH-ORDER',
        })
        self.assertFalse(picking.related_purchase_id)
        self.assertFalse(picking.related_sale_id)
