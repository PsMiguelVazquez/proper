# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestStockQuantClient(TransactionCase):

    def test_compute_costo_cliente_without_studio_fields_does_not_crash(self):
        product = self.env['product.product'].create({
            'name': 'Quant Client Test Product',
            'type': 'consu',
            'is_storable': True,
        })
        location = self.env['stock.location'].search([('usage', '=', 'internal')], limit=1)
        quant = self.env['stock.quant'].create({
            'product_id': product.id,
            'location_id': location.id,
            'quantity': 5.0,
        })
        # sin wizard de cliente creado, ni campos de Studio: no debe fallar
        self.assertEqual(quant.cliente_reporte, '')
        self.assertEqual(quant.margen_cliente, 0.0)
        self.assertEqual(quant.costo_cliente, 0.0)

    def test_wizard_change_report_client(self):
        partner = self.env['res.partner'].create({'name': 'Quant Client Test Partner'})
        wizard = self.env['change.client.wizard'].create({'client_id': partner.id})
        self.assertTrue(wizard.change_report_client())
