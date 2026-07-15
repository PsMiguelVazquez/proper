# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestCrmLead(TransactionCase):

    def setUp(self):
        super().setUp()
        self.source = self.env['utm.source'].create({'name': 'Test Source'})
        self.valid_vals = {
            'name': 'Test Opportunity',
            'contact_name': 'John Doe',
            'email_from': 'john@example.com',
            'phone': '123456',
            'source_id': self.source.id,
        }

    def test_create_requires_contact_name(self):
        vals = dict(self.valid_vals, contact_name=False)
        with self.assertRaises(ValidationError):
            self.env['crm.lead'].create(vals)

    def test_create_requires_email(self):
        vals = dict(self.valid_vals, email_from=False)
        with self.assertRaises(ValidationError):
            self.env['crm.lead'].create(vals)

    def test_create_requires_phone(self):
        vals = dict(self.valid_vals, phone=False)
        with self.assertRaises(ValidationError):
            self.env['crm.lead'].create(vals)

    def test_create_requires_source(self):
        vals = dict(self.valid_vals, source_id=False)
        with self.assertRaises(ValidationError):
            self.env['crm.lead'].create(vals)

    def test_create_succeeds_with_all_required_fields(self):
        lead = self.env['crm.lead'].create(self.valid_vals)
        self.assertTrue(lead)

    def test_write_blocks_clearing_contact_name(self):
        lead = self.env['crm.lead'].create(self.valid_vals)
        with self.assertRaises(ValidationError):
            lead.write({'contact_name': ''})

    def test_onchange_partner_without_studio_fields_does_not_crash(self):
        partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'origen': self.source.id,
        })
        lead = self.env['crm.lead'].new(self.valid_vals)
        lead.partner_id = partner
        lead._completa_info_cliente()
        self.assertEqual(lead.contact_name, partner.name)
        self.assertEqual(lead.source_id, self.source)

    def test_es_admin_default_false(self):
        lead = self.env['crm.lead'].create(self.valid_vals)
        self.assertFalse(lead.es_admin)
