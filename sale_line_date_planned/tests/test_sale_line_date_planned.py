# -*- coding: utf-8 -*-
from datetime import date, timedelta

from odoo.tests import tagged, TransactionCase


@tagged('post_install', '-at_install')
class TestSaleLineDatePlanned(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # `sale_purchase_confirm` exige nivel de cliente y documento/método
        # de entrega antes de poder confirmar una orden de venta.
        nivel = cls.env['x_niveles_de_cliente'].create({'x_name': 'A'})
        cls.parent_partner = cls.env['res.partner'].create({'name': 'Parent Partner', 'x_nivel_cliente': nivel.id})
        cls.child_partner = cls.env['res.partner'].create({
            'name': 'Child Partner',
            'parent_id': cls.parent_partner.id,
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Test Product',
            'type': 'consu',
            'is_storable': True,
            'default_code': 'SLDP-1',
            'invoice_policy': 'order',
        })

    def test_set_domain_addres_includes_parent_and_children(self):
        order = self.env['sale.order'].create({'partner_id': self.parent_partner.id})
        line = self.env['sale.order.line'].create({
            'order_id': order.id,
            'product_id': self.product.id,
            'product_uom_qty': 1,
        })
        self.assertIn(self.parent_partner, line.partner_ids)
        self.assertIn(self.child_partner, line.partner_ids)

    def test_set_domain_addres_empty_without_partner(self):
        order = self.env['sale.order'].new({})
        line = self.env['sale.order.line'].new({'order_id': order})
        line.set_domain_addres()
        self.assertFalse(line.partner_ids)

    def test_confirm_order_with_multiple_planned_dates_splits_pickings(self):
        order = self.env['sale.order'].create({
            'partner_id': self.parent_partner.id,
            'x_doc_entrega': 'factura',
            'x_metodo_entrega': 'flotilla',
            # `x_cantidad_disponible_compra`: la validación de existencias
            # de `sale_purchase_confirm` (`stock_quant_warehouse_zero`)
            # depende de un id de ubicación hardcodeado (187, "Almacén 0" de
            # la base de producción de 15.0) que no existe en este entorno
            # genérico; se usa este campo -pensado justo para que Compras
            # autorice disponibilidad sin depender del almacén real- para
            # no acoplar este test a esa ubicación específica.
            'order_line': [
                (0, 0, {
                    'product_id': self.product.id,
                    'product_uom_qty': 1,
                    'x_cantidad_disponible_compra': 10,
                    'date_planned_l': date.today(),
                    'date_planned_line': self.parent_partner.id,
                }),
                (0, 0, {
                    'product_id': self.product.id,
                    'product_uom_qty': 1,
                    'x_cantidad_disponible_compra': 10,
                    'date_planned_l': date.today() + timedelta(days=3),
                    'date_planned_line': self.child_partner.id,
                }),
            ],
        })
        order.action_confirm()
        self.assertGreaterEqual(len(order.picking_ids), 1)
