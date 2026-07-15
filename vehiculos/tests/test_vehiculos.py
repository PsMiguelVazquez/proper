# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestVehiculos(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.marca = cls.env['marca.automovil'].create({'name': 'Test Marca'})
        cls.modelo = cls.env['modelo.automovil'].create({'name': 'Test Modelo', 'marca_id': cls.marca.id})
        cls.driver = cls.env['res.partner'].create({'name': 'Test Driver'})
        cls.automovil = cls.env['automovil'].create({
            'name': 'Test Car',
            'modelo': cls.modelo.id,
            'driver_id': cls.driver.id,
        })

    def test_automovil_creation_and_related_logo(self):
        self.assertEqual(self.automovil.modelo, self.modelo)
        # el logo se relaciona modelo -> marca
        self.assertFalse(self.automovil.imagen)

    def test_creacion_ruta_sets_sequence_name(self):
        ruta = self.env['creacion.ruta'].create({'tipo': 'local'})
        self.assertTrue(ruta.name)
        self.assertNotEqual(ruta.name, 'New')

    def test_confirmar_without_orders_raises(self):
        ruta = self.env['creacion.ruta'].create({'tipo': 'local'})
        with self.assertRaises(UserError):
            ruta.confirmar()

    def test_dominio_onchange_does_not_crash(self):
        ruta = self.env['creacion.ruta'].new({'tipo': 'local'})
        result = ruta.dominio()
        self.assertIn('domain', result)
        self.assertIn('ordenes', result['domain'])

    def test_stock_picking_write_propagates_tracking_ref_to_sale(self):
        partner = self.env['res.partner'].create({'name': 'Vehiculos Test Partner'})
        sale_order = self.env['sale.order'].create({'partner_id': partner.id})
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)], limit=1)
        picking = self.env['stock.picking'].create({
            'picking_type_id': warehouse.out_type_id.id,
            'location_id': warehouse.lot_stock_id.id,
            'location_dest_id': warehouse.out_type_id.default_location_dest_id.id,
            'sale_id': sale_order.id,
        })
        picking.write({'carrier_tracking_ref': 'TRACK-123'})
        self.assertEqual(sale_order.carrier_tracking_ref, 'TRACK-123')

    def test_sale_order_write_propagates_guia_to_pickings(self):
        partner = self.env['res.partner'].create({'name': 'Vehiculos Test Partner 2'})
        sale_order = self.env['sale.order'].create({'partner_id': partner.id})
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)], limit=1)
        picking = self.env['stock.picking'].create({
            'picking_type_id': warehouse.out_type_id.id,
            'location_id': warehouse.lot_stock_id.id,
            'location_dest_id': warehouse.out_type_id.default_location_dest_id.id,
            'sale_id': sale_order.id,
        })
        sale_order.write({'guia': 'GUIA-456'})
        self.assertEqual(picking.guia, 'GUIA-456')
