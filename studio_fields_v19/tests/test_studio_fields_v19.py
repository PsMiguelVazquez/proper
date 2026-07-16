# -*- coding: utf-8 -*-
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestStudioFieldsV19(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Studio Fields Test Partner'})
        cls.product = cls.env['product.product'].create(
            {'name': 'Studio Fields Test Product', 'type': 'consu', 'list_price': 100.0})

    def test_sale_order_aggregate_fields_do_not_crash(self):
        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 2,
                'price_unit': 50.0,
            })],
        })
        self.assertEqual(order.x_studio_cant_x_entregar, 2)
        self.assertEqual(order.x_sale_id_stock_picking_count, 0)
        self.assertEqual(order.x_sale__stock_picking_count, 0)

    def test_sale_order_line_price_fields(self):
        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 2,
                'price_unit': 50.0,
            })],
        })
        line = order.order_line[0]
        self.assertEqual(line.x_precio_iva, 58.0)
        self.assertEqual(line.x_subtotal_iva, 116.0)

    def test_crm_lead_probabilidad_without_mobile_field(self):
        # MIGRACIÓN V19: regresión para el fix de `mobile`, que ya no existe
        # en crm.lead (ver models/crm_lead.py).
        source = self.env['utm.source'].create({'name': 'Test source'})
        lead = self.env['crm.lead'].create({
            'name': 'Studio Lead Test', 'partner_id': self.partner.id, 'contact_name': 'Juan',
            'phone': '555', 'email_from': 'a@b.com', 'source_id': source.id,
        })
        self.assertEqual(lead.x_probabilidad_lead, 10)

    def test_product_template_volume_fields(self):
        tmpl = self.product.product_tmpl_id
        tmpl.write({
            'x_studio_alto_c_m': 2, 'x_studio_ancho_c_m': 3, 'x_studio_largo_c_m': 4,
            'x_Al': 1, 'x_An': 2, 'x_La': 3,
        })
        self.assertEqual(tmpl.x_studio_volumen_c_m, 24.0)
        self.assertEqual(tmpl.x_vol, 6.0)

    def test_res_partner_counts_do_not_crash(self):
        self.assertEqual(self.partner.x_partner_id_account_move_count, 0)
        self.assertEqual(self.partner.x_x_holding__res_partner_count, 0)
