# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestPartnerAccountCreditor(TransactionCase):

    def test_property_account_creditor_field(self):
        account = self.env['account.account'].search([], limit=1)
        partner = self.env['res.partner'].create({
            'name': 'Creditor Test Partner',
            'property_account_creditor': account.id,
        })
        self.assertEqual(partner.property_account_creditor, account)
