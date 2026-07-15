# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestHelpdeskTicket(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.team = cls.env['helpdesk.team'].search([], limit=1)
        cls.user = cls.env.ref('base.user_admin')
        cls.ticket = cls.env['helpdesk.ticket'].create({
            'name': 'Test ticket',
            'team_id': cls.team.id,
        })

    def test_write_schedules_assignment_activity(self):
        self.ticket.write({'user_id': self.user.id})
        activity_type = self.env.ref('mail.mail_activity_data_todo')
        activity = self.env['mail.activity'].search([
            ('res_id', '=', self.ticket.id),
            ('res_model', '=', 'helpdesk.ticket'),
            ('activity_type_id', '=', activity_type.id),
            ('summary', '=', 'Ticket asignado'),
        ])
        self.assertTrue(activity)

    def test_write_does_not_duplicate_activity(self):
        self.ticket.write({'user_id': self.user.id})
        self.ticket.write({'name': 'Test ticket renamed'})
        activity_type = self.env.ref('mail.mail_activity_data_todo')
        activities = self.env['mail.activity'].search([
            ('res_id', '=', self.ticket.id),
            ('res_model', '=', 'helpdesk.ticket'),
            ('activity_type_id', '=', activity_type.id),
            ('summary', '=', 'Ticket asignado'),
        ])
        self.assertEqual(len(activities), 1)

    def test_partner_defaults_from_sale_order(self):
        partner = self.env['res.partner'].create({'name': 'Helpdesk Test Partner'})
        sale_order = self.env['sale.order'].create({'partner_id': partner.id})
        ticket = self.env['helpdesk.ticket'].new({'name': 'Test ticket 2', 'team_id': self.team.id})
        ticket.sale_order_id = sale_order
        ticket._get_default_partner_id()
        self.assertEqual(ticket.partner_id, partner)
