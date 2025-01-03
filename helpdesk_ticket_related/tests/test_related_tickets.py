# Copyright 2024 Antoni Marroig(APSL-Nagarro)<amarroig@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class HelpdeskTicketRelatedTickets(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ticket1 = cls.env.ref("helpdesk_mgmt.helpdesk_ticket_1")
        cls.ticket2 = cls.env.ref("helpdesk_mgmt.helpdesk_ticket_2")

    def test_link_tickets(self):
        self.ticket1.related_ticket_ids = [(4, self.ticket2.id)]
        self.assertEqual(self.ticket2.related_ticket_ids, self.ticket1)

    def test_unlink_tickets(self):
        self.ticket1.related_ticket_ids = [(4, self.ticket2.id)]
        self.ticket1.related_ticket_ids = [[6, False, []]]
        self.assertEqual(self.ticket2.related_ticket_ids.ids, [])

    def test_open_ticket(self):
        self.assertEqual(
            self.ticket1.open_ticket(),
            {
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "res_model": "helpdesk.ticket",
                "res_id": self.ticket1.id,
            },
        )
