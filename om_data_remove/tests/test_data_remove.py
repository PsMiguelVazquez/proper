# -*- coding: utf-8 -*-
from unittest.mock import patch

from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestDataRemove(TransactionCase):

    def test_remove_data_ignores_unknown_model(self):
        wizard = self.env['res.config.settings'].create({})
        # must not raise even if the model doesn't exist
        self.assertTrue(wizard.remove_data(['this.model.does.not.exist']))

    def test_reset_cat_loc_name(self):
        wizard = self.env['res.config.settings'].create({})
        self.assertTrue(wizard.reset_cat_loc_name())

    def test_remove_message_deletes_plain_message(self):
        partner = self.env['res.partner'].create({'name': 'Data Remove Test Partner'})
        message = self.env['mail.message'].create({
            'model': 'res.partner',
            'res_id': partner.id,
            'message_type': 'comment',
            'body': 'scratch message for data-remove test',
        })
        self.assertTrue(message.exists())
        wizard = self.env['res.config.settings'].create({})
        # `remove_data` commits after each raw DELETE, which Odoo's test
        # cursor deliberately forbids (it would break the test's rollback
        # isolation). Neutralize just the commit for this test: the DELETE
        # itself still runs for real on the test's savepoint.
        with patch.object(self.cr, 'commit'):
            wizard.remove_message()
        message.invalidate_recordset()
        self.assertFalse(message.exists())
