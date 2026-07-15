# -*- coding: utf-8 -*-
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.exceptions import UserError
from odoo.tests import tagged

# MIGRACIÓN V19: `refactura_credito`/`create_in`/`create_out` dependen de un
# almacén con `location_dest_id`/`location_id` hardcodeado en 69 (el
# "ALM-9" de refacturación de la base de producción de 15.0, ver nota en
# `models/account_move.py`), que no existe en este entorno de pruebas
# genérico. Estos tests cubren las validaciones de `refactura_credito()`
# que se ejecutan ANTES de llegar a esos movimientos de almacén; los
# caminos que sí tocan `create_in`/`create_out` requieren la configuración
# real del almacén de refacturación del entorno de destino.


@tagged('post_install', '-at_install')
class TestRefacturacion(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_partner = cls.env['res.partner'].create({'name': 'Refacturacion Other Partner'})

    def test_es_refacturacion_default_false(self):
        invoice = self.init_invoice('out_invoice', products=self.product_a and [self.product_a] or None)
        self.assertFalse(invoice.es_refacturacion)

    def test_refactura_credito_requires_es_refacturacion(self):
        credit_note = self.init_invoice('out_refund', products=self.product_a and [self.product_a] or None)
        credit_note.action_post()
        with self.assertRaises(UserError):
            credit_note.with_context(active_ids=credit_note.ids).refactura_credito()

    def test_refactura_credito_requires_credit_note_type(self):
        invoice = self.init_invoice('out_invoice', products=self.product_a and [self.product_a] or None)
        invoice.es_refacturacion = True
        invoice.action_post()
        with self.assertRaises(UserError):
            invoice.with_context(active_ids=invoice.ids).refactura_credito()

    def test_refactura_credito_requires_posted_state(self):
        credit_note = self.init_invoice('out_refund', products=self.product_a and [self.product_a] or None)
        credit_note.es_refacturacion = True
        with self.assertRaises(UserError):
            credit_note.with_context(active_ids=credit_note.ids).refactura_credito()

    def test_refactura_credito_requires_single_partner(self):
        credit_note1 = self.init_invoice('out_refund', products=self.product_a and [self.product_a] or None)
        credit_note1.es_refacturacion = True
        credit_note1.action_post()
        credit_note2 = self.init_invoice('out_refund', partner=self.other_partner, products=self.product_a and [self.product_a] or None)
        credit_note2.es_refacturacion = True
        credit_note2.action_post()
        with self.assertRaises(UserError):
            (credit_note1 | credit_note2).with_context(active_ids=(credit_note1 | credit_note2).ids).refactura_credito()
