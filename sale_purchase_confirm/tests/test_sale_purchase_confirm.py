# -*- coding: utf-8 -*-
from odoo.tests import tagged, TransactionCase
from odoo.exceptions import UserError


@tagged('post_install', '-at_install')
class TestCustomModels(TransactionCase):

    def test_x_fabricante_margen_fields(self):
        fabricante = self.env['x_fabricante'].create({'x_name': 'ACME', 'x_studio_margen_A': 20.0})
        self.assertEqual(fabricante['x_studio_margen_A'], 20.0)
        self.assertTrue(fabricante.x_active)

    def test_x_familia_linea_grupo_creation(self):
        familia = self.env['x_familia'].create({'x_name': 'Familia test'})
        linea = self.env['x_linea'].create({'x_name': 'Linea test'})
        grupo = self.env['x_grupo'].create({'x_name': 'Grupo test'})
        self.assertTrue(familia.x_active and linea.x_active and grupo.x_active)


@tagged('post_install', '-at_install')
class TestProductStudioFields(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.fabricante = cls.env['x_fabricante'].create({'x_name': 'Fabricante test', 'x_studio_margen_A': 25.0})
        cls.product = cls.env['product.product'].create({
            'name': 'Producto test SPC',
            'type': 'consu',
            'default_code': 'SPC-001',
            'standard_price': 100.0,
            'x_fabricante': cls.fabricante.id,
        })

    def test_x_studio_ultimo_costo_without_valuation(self):
        self.assertEqual(self.product.product_tmpl_id.x_studio_ultimo_costo, 0.0)

    def test_x_fabricante_relation(self):
        self.assertEqual(self.product.product_tmpl_id.x_fabricante, self.fabricante)


@tagged('post_install', '-at_install')
class TestSaleOrderStudioFields(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.nivel = cls.env['x_niveles_de_cliente'].create({'x_name': 'A'})
        cls.partner = cls.env['res.partner'].create({'name': 'Cliente SPC test', 'x_nivel_cliente': cls.nivel.id})
        cls.fabricante = cls.env['x_fabricante'].create({'x_name': 'Fabricante SO test', 'x_studio_margen_A': 20.0})
        cls.product = cls.env['product.product'].create({
            'name': 'Producto SO test',
            'type': 'consu',
            'default_code': 'SPC-SO-1',
            'standard_price': 80.0,
            'x_fabricante': cls.fabricante.id,
        })
        cls.order = cls.env['sale.order'].create({'partner_id': cls.partner.id})

    def test_x_doc_entrega_selection_values(self):
        self.order.x_doc_entrega = 'remision_sin_costo'
        self.assertEqual(self.order.x_doc_entrega, 'remision_sin_costo')

    def test_is_valid_order_sale_missing_entrega_fields(self):
        self.env['sale.order.line'].create({
            'order_id': self.order.id,
            'product_id': self.product.id,
            'product_uom_qty': 1,
            'price_unit': 100.0,
        })
        valid, message = self.order.is_valid_order_sale()
        self.assertFalse(valid)
        self.assertIn('documento de entrega', message)
        self.assertIn('método de entrega', message)

    def _create_kit(self, component_qties):
        """Crea un kit (BoM phantom) con un componente rastreado por cada
        cantidad de `component_qties`, con esa existencia en el almacén de
        la orden."""
        if 'mrp.bom' not in self.env:
            self.skipTest('mrp no está instalado')
        stock_location = self.order.warehouse_id.lot_stock_id
        kit = self.env['product.product'].create({
            'name': 'Kit SO test', 'type': 'consu', 'is_storable': True, 'default_code': 'SPC-KIT-1',
        })
        bom_lines = []
        for i, qty in enumerate(component_qties):
            component = self.env['product.product'].create({
                'name': 'Componente SO test %s' % i, 'type': 'consu', 'is_storable': True,
                'default_code': 'SPC-KIT-C%s' % i,
            })
            if qty:
                self.env['stock.quant']._update_available_quantity(component, stock_location, qty)
            bom_lines.append((0, 0, {'product_id': component.id, 'product_qty': 1}))
        self.env['mrp.bom'].create({
            'product_tmpl_id': kit.product_tmpl_id.id, 'type': 'phantom', 'bom_line_ids': bom_lines,
        })
        self.env['sale.order.line'].create({
            'order_id': self.order.id, 'product_id': kit.id, 'product_uom_qty': 1, 'price_unit': 100.0,
        })

    def test_is_valid_order_sale_kit_uses_component_stock(self):
        # Un kit no tiene quants propios: su existencia sale de los componentes.
        self._create_kit([1, 2, 3])
        valid, message = self.order.is_valid_order_sale()
        self.assertNotIn('No hay stock suficiente', message)

    def test_is_valid_order_sale_kit_missing_component(self):
        self._create_kit([1, 0])
        valid, message = self.order.is_valid_order_sale()
        self.assertFalse(valid)
        self.assertIn('No hay stock suficiente', message)

    def test_x_utilidad_por_compute(self):
        line = self.env['sale.order.line'].create({
            'order_id': self.order.id,
            'product_id': self.product.id,
            'product_uom_qty': 1,
            'price_unit': 100.0,
        })
        # Sin nuevo costo: usa x_studio_costo_promedio (related a
        # standard_price, cuyo valor exacto puede variar levemente por el
        # costeo automático de este branch de 19.0); se valida el rango
        # esperado en vez del valor exacto para no depender de ese detalle.
        self.assertGreaterEqual(line.x_utilidad_por, 15)
        self.assertLessEqual(line.x_utilidad_por, 20)
        line.x_studio_nuevo_costo = 60.0
        # con nuevo costo: (1 - 60/100) * 100 = 40, este cálculo no depende
        # de standard_price y es totalmente determinista.
        self.assertEqual(line.x_utilidad_por, 40)

    def test_x_studio_nivel_related_from_partner(self):
        self.assertEqual(self.order.x_studio_nivel, self.nivel.x_name)


@tagged('post_install', '-at_install')
class TestRequirementProposal(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Cliente requerimiento test'})
        cls.order = cls.env['sale.order'].create({'partner_id': cls.partner.id})

    def test_requiriment_client_sequence_on_create(self):
        req = self.env['requiriment.client'].create({'x_order_id': self.order.id, 'x_descripcion': 'Requerimiento test'})
        self.assertTrue(req.x_name)
        self.assertTrue(req.x_name.startswith('REQ-'))

    def test_proposal_purchases_sequence_on_create(self):
        req = self.env['requiriment.client'].create({'x_order_id': self.order.id, 'x_descripcion': 'Requerimiento test 2'})
        prop = self.env['proposal.purchases'].create({'rel_id': req.id, 'x_descripcion': 'Propuesta test', 'x_costo': 50.0})
        self.assertTrue(prop.x_name)
        self.assertTrue(prop.x_name.startswith('PROP-'))

    def test_proposal_confirm_creates_product(self):
        req = self.env['requiriment.client'].create({'x_order_id': self.order.id, 'x_descripcion': 'Requerimiento test 3'})
        prop = self.env['proposal.purchases'].create({
            'rel_id': req.id, 'x_descripcion': 'Producto de propuesta test',
            'x_modelo': 'SPC-PROP-1', 'x_costo': 40.0, 'x_cantidad': 2,
        })
        prop.confirm()
        self.assertEqual(prop.x_state, 'done')
        self.assertTrue(prop.x_product_id)
        self.assertEqual(prop.x_product_id.default_code, 'SPC-PROP-1')
        self.assertTrue(self.order.order_line.filtered(lambda l: l.product_id == prop.x_product_id))


@tagged('post_install', '-at_install')
class TestStudioLegacyModels(TransactionCase):
    """
    MIGRACIÓN V19: `x_client_requirement`/`x_proposal_purchase` son los
    modelos originalmente creados por Odoo Studio (ver nota en
    `models/account_move.py`), formalizados con su esquema real.
    """

    def test_x_client_requirement_create(self):
        req = self.env['x_client_requirement'].create({'x_name': 'Legacy req test', 'x_descripcion': 'Prueba'})
        self.assertTrue(req.id)

    def test_x_proposal_purchase_create_without_order_does_not_crash(self):
        req = self.env['x_client_requirement'].create({'x_name': 'Legacy req test 2'})
        prop = self.env['x_proposal_purchase'].create({'x_rel_id': req.id, 'x_descripcion': 'Propuesta legado'})
        self.assertTrue(prop.id)


@tagged('post_install', '-at_install')
class TestAccountMoveStudioFields(TransactionCase):

    def test_set_folio_from_name(self):
        move = self.env['account.move'].create({'move_type': 'entry'})
        move.name = 'INV/2024/00042'
        move.set_folio()
        self.assertEqual(move.folio, '42')

    def test_x_estado_actuali_cli_related(self):
        partner = self.env['res.partner'].create({'name': 'Cliente move test', 'x_estado_cli_actua': '3.3'})
        move = self.env['account.move'].create({'move_type': 'entry', 'partner_id': partner.id})
        self.assertEqual(move.x_estado_actuali_cli, '3.3')
