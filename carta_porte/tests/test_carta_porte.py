# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo.tests import tagged, TransactionCase


@tagged('post_install', '-at_install')
class TestCartaPorte(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Carta Porte Test Partner'})

    def test_get_cfi_use_without_attachments(self):
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner.id,
        })
        self.assertEqual(invoice.use_cfdi, '')

    def test_delivery_guide_requires_done_quantities(self):
        picking_type_out = self.env.ref('stock.picking_type_out')
        picking = self.env['stock.picking'].create({
            'partner_id': self.partner.id,
            'picking_type_id': picking_type_out.id,
            'location_id': picking_type_out.default_location_src_id.id,
            'location_dest_id': picking_type_out.default_location_dest_id.id,
        })
        with self.assertRaises(UserError):
            picking.l10n_mx_edi_cfdi_try_send()
