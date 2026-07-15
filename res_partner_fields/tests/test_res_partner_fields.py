# -*- coding: utf-8 -*-
from odoo.tests import tagged, TransactionCase


@tagged('post_install', '-at_install')
class TestResPartnerFields(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Res Partner Fields Test'})

    def test_codigo_uso_cfdi_compute(self):
        self.partner.x_studio_uso_de_cfdi = 'G01'
        self.assertEqual(self.partner.codigo_uso_cfdi, 'G01')
        self.partner.x_studio_uso_de_cfdi = False
        self.assertEqual(self.partner.codigo_uso_cfdi, '')

    def test_codigo_metodo_pago_compute(self):
        method = self.env['l10n_mx_edi.payment.method'].search([], limit=1)
        self.partner.x_studio_mtodo_de_pago = method
        self.assertEqual(self.partner.codigo_metodo_pago, method.code)
        self.partner.x_studio_mtodo_de_pago = False
        self.assertEqual(self.partner.codigo_metodo_pago, '')

    def test_nom_corto_agente_venta_compute(self):
        agent = self.env['res.users'].search([], limit=1)
        agent.x_studio_clave_del_vendedor_1 = 'V001'
        self.partner.sales_agent = agent
        self.assertEqual(self.partner.x_nom_corto_agente_venta, 'V001')

    def test_nombre_corto_tpago_related(self):
        term = self.env['account.payment.term'].search([], limit=1)
        term.x_nombre_corto = 'PUE'
        self.partner.property_payment_term_id = term
        self.assertEqual(self.partner.x_nombre_corto_tpago, 'PUE')

    def test_on_change_categoria_does_not_crash_without_team_id(self):
        # `team_id` no existe en `res.partner` (ver nota en el modelo); el
        # onchange debe simplemente no hacer nada, sin fallar.
        categoria = self.env['x_categoria_compania'].create({'x_name': 'Studio Category Team'})
        self.partner.x_cat_com = categoria
        self.partner._on_change_categoria()

    def test_payment_method_display_name(self):
        method = self.env['l10n_mx_edi.payment.method'].search([], limit=1)
        self.assertIn(method.code, method.display_name)
        self.assertEqual(
            method.with_context(hide_code=True).display_name, method.name
        )

    def test_on_change_property_account_position_sets_fiscal_regime(self):
        fiscal_position = self.env['account.fiscal.position'].create({
            'name': '601- General de Ley Personas Morales',
        })
        self.partner.property_account_position_id = fiscal_position
        self.partner._on_change_property_account_position_id()
        self.assertEqual(self.partner.l10n_mx_edi_fiscal_regime, '601')
