# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestKardexProductos(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env['stock.warehouse'].search([('company_id', '=', cls.env.company.id)], limit=1)
        cls.product = cls.env['product.product'].create({
            'name': 'Kardex Test Product',
            'type': 'consu',
            'is_storable': True,
        })
        cls.inventory_loc = cls.env['stock.location'].search([
            ('usage', '=', 'inventory'), ('company_id', '=', cls.env.company.id),
        ], limit=1)
        cls.stock_loc = cls.warehouse.lot_stock_id

    def _validate_move(self, picking_type, src_loc, dst_loc, qty):
        picking = self.env['stock.picking'].create({
            'picking_type_id': picking_type.id,
            'location_id': src_loc.id,
            'location_dest_id': dst_loc.id,
        })
        self.env['stock.move'].create({
            'picking_id': picking.id,
            'product_id': self.product.id,
            'product_uom_qty': qty,
            'product_uom': self.product.uom_id.id,
            'location_id': src_loc.id,
            'location_dest_id': dst_loc.id,
        })
        picking.action_confirm()
        for move in picking.move_ids:
            move.quantity = qty
            move.picked = True
        picking.button_validate()
        return picking

    def test_kardex_computes_without_error_and_tracks_balance(self):
        # Entrada por ajuste de inventario: WH/Stock queda con `qty` unidades.
        in_picking = self._validate_move(
            self.warehouse.in_type_id, self.inventory_loc, self.stock_loc, 10.0
        )
        in_line = in_picking.move_line_ids
        self.assertEqual(in_line.entradas_destino, 10.0)
        self.assertEqual(in_line.saldo_destino, 10.0)

        # Salida (entrega a cliente): el saldo de origen debe descontar la salida.
        customer_loc = self.warehouse.out_type_id.default_location_dest_id
        out_picking = self._validate_move(
            self.warehouse.out_type_id, self.stock_loc, customer_loc, 4.0
        )
        out_line = out_picking.move_line_ids
        self.assertEqual(out_line.salidas_origen, 4.0)
        self.assertAlmostEqual(out_line.saldo_origen, 6.0, places=2)
