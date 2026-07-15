# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestDecimalPrecision(TransactionCase):

    def test_company_display_digits_default(self):
        self.assertEqual(self.env.company.display_digits, 2)

    def test_float_rounds_to_company_display_digits(self):
        """ Float/Monetary storage precision must follow res.company.display_digits,
        regardless of the digits configured on the field itself (see models/fields.py). """
        self.env.company.display_digits = 3
        currency = self.env.ref('base.USD')
        rate = self.env['res.currency.rate'].create({
            'currency_id': currency.id,
            'rate': 1.123456789,
        })
        self.assertEqual(rate.rate, 1.123)
        # force a DB round-trip to make sure the rounding also holds for convert_to_column
        rate.invalidate_recordset()
        self.assertEqual(rate.rate, 1.123)

    def test_currency_round_uses_company_display_digits(self):
        self.env.company.display_digits = 1
        currency = self.env.ref('base.USD')
        self.assertEqual(currency.round(3.14159), 3.1)
