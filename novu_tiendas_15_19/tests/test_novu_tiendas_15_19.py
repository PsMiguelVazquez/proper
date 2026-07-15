# -*- coding: utf-8 -*-
from odoo.tests import tagged, TransactionCase


@tagged('post_install', '-at_install')
class TestNovuTiendas1519(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ws_tienda = cls.env['ws.tienda']
        cls.source = cls.env['utm.source'].create({'name': 'Test Source'})

    def _lead_base_vals(self):
        return {
            'contact_name': 'Contacto Test',
            'email_from': 'test@example.com',
            'phone': '123456',
            'source_id': self.source.id,
        }

    def test_create_lead_sets_description_from_mensaje(self):
        lead = self.env['crm.lead'].create({
            **self._lead_base_vals(),
            'name': 'Test Lead',
            'captado_en': 'PROPER V19',
            'mensaje': 'Interesado en producto X',
        })
        self.assertIn('Interesado en producto X', lead.description)

    def test_create_lead_without_proper_v19_source_keeps_defaults(self):
        lead = self.env['crm.lead'].create({
            **self._lead_base_vals(),
            'name': 'Other Lead',
            'captado_en': 'Otro origen',
            'mensaje': 'Mensaje que no debe copiarse',
        })
        self.assertFalse(lead.description)

    def test_obtener_categoria_producto(self):
        resp = self.ws_tienda.ObtenerCategoriaProducto()
        self.assertTrue(resp['procesada'])
        self.assertIsInstance(resp['catalogo'], list)

    def test_obtener_productos_tienda_proper(self):
        product_tmpl = self.env['product.template'].create({
            'name': 'Producto Proper Test',
            'proper': True,
            'sale_ok': True,
        })
        resp = self.ws_tienda.ObtenerProductosTiendaProper()
        self.assertTrue(resp['procesada'])
        ids = [p['id'] for p in resp['catalogo']]
        self.assertIn(product_tmpl.product_variant_id.id, ids)

    def test_crear_oportunidad(self):
        resp = self.ws_tienda.CrearOportunidad({
            'infoOportunidad': {
                'name': 'Oportunidad Test',
                'email_from': 'test@example.com',
                'phone': '123456',
                'contact_name': 'Contacto Test',
                'source_id': self.source.id,
                'captado_en': 'Web',
                'mensaje': 'Quiero información',
            }
        })
        self.assertTrue(resp['procesada'], resp)
        lead = self.env['crm.lead'].browse(resp['catalogo'][0]['id'])
        self.assertEqual(lead.name, 'Oportunidad Test')
