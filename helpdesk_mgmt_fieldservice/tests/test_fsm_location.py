# Copyright (C) 2022 Trevi Software
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import Form

from . import common


class TestFSMOrder(common.TestHelpdeskFieldservice):
    def test_ticket_count(self):

        self.test_partner.service_location_id = self.test_location
        self.assertEqual(
            self.test_location.ticket_count,
            0,
            "Initially, the ticket count on the location is zero",
        )

        with Form(self.ticket) as f:
            f.partner_id = self.test_partner

        self.assertEqual(
            self.test_location.ticket_count,
            1,
            "The ticket count on the location increases after creation of ticket",
        )

        res = self.test_location.action_view_ticket()
        self.assertEqual(
            res["res_id"],
            self.ticket.id,
            "With only 1 ticket, we go directly to the ticket",
        )

        ticket2 = self.Ticket.create(
            {
                "name": "Test 2",
                "description": "Ticket test 2",
                "fsm_location_id": self.test_location.id,
                "partner_id": self.test_partner.id,
            }
        )
        res = self.test_location.action_view_ticket()

        self.assertEqual(
            res["domain"],
            [("id", "in", [ticket2.id, self.ticket.id])],
            "With multiple tickets we go to list view",
        )
