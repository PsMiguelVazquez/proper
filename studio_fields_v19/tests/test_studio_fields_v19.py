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
        # MIGRACIÓN V19: estos computes no tienen `@api.depends` a propósito
        # (ver models/common.py) porque sus dependencias son campos de
        # Studio que pueden no existir en todas las bases; por eso sólo se
        # calculan al crear el registro, no en cada `write` posterior -se
        # crea ya con los valores en vez de escribirlos después-.
        tmpl = self.env['product.template'].create({
            'name': 'Studio Fields Volume Test Product',
            'type': 'consu',
            'x_studio_alto_c_m': 2, 'x_studio_ancho_c_m': 3, 'x_studio_largo_c_m': 4,
            'x_Al': 1, 'x_An': 2, 'x_La': 3,
        })
        self.assertEqual(tmpl.x_studio_volumen_c_m, 24.0)
        self.assertEqual(tmpl.x_vol, 6.0)

    def test_res_partner_counts_do_not_crash(self):
        self.assertEqual(self.partner.x_partner_id_account_move_count, 0)
        self.assertEqual(self.partner.x_x_holding__res_partner_count, 0)

    def test_fix_broken_payment_receipt_post_time_ref(self):
        # MIGRACIÓN V19: reproduce en miniatura el bug real de la
        # personalización de Studio del reporte "Complemento de Pago"
        # (o.l10n_mx_edi_post_time, campo inexistente en account.payment -
        # solo existe en account.move vía move_id-) y confirma que el
        # self-heal lo corrige sin tocar nada más de la vista.
        from .. import _fix_broken_payment_receipt_post_time_ref

        view = self.env['ir.ui.view'].create({
            'name': 'Studio Fields Test - Complemento de Pago roto',
            'type': 'qweb',
            'arch_db': (
                '<div><span t-field="o.l10n_mx_edi_post_time"/>'
                '<span t-field="o.move_id.l10n_mx_edi_cfdi_uuid"/></div>'
            ),
        })
        _fix_broken_payment_receipt_post_time_ref(self.env)
        view.invalidate_recordset(['arch_db'])
        self.assertIn('o.move_id.l10n_mx_edi_post_time', view.arch_db)
        self.assertNotIn('t-field="o.l10n_mx_edi_post_time"', view.arch_db)
        # No debe alterar referencias que ya estaban correctas.
        self.assertIn('o.move_id.l10n_mx_edi_cfdi_uuid', view.arch_db)

        # Idempotente: correrlo de nuevo no debe romper ni duplicar el prefijo.
        _fix_broken_payment_receipt_post_time_ref(self.env)
        view.invalidate_recordset(['arch_db'])
        self.assertEqual(view.arch_db.count('l10n_mx_edi_post_time'), 1)
