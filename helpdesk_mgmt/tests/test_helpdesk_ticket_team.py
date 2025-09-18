# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo.tests.common import users

from .common import TestHelpdeskTicketBase


class TestHelpdeskTicketTeam(TestHelpdeskTicketBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Model = cls.env["helpdesk.ticket.team"]
        cls.root = cls.Model.create(
            {
                "name": "Root",
            }
        )
        cls.child = cls.Model.create(
            {
                "name": "Child",
                "parent_id": cls.root.id,
            }
        )
        cls.grandchild = cls.Model.create(
            {
                "name": "Grandchild",
                "parent_id": cls.child.id,
            }
        )

    def test_complete_name_computation(self):
        self.assertEqual(self.root.complete_name, "Root")
        self.assertEqual(self.child.complete_name, "Root / Child")
        self.assertEqual(self.grandchild.complete_name, "Root / Child / Grandchild")

    @users("helpdesk_mgmt-user_own")
    def test_helpdesk_ticket_user_own(self):
        tickets = self.env["helpdesk.ticket"].search([])
        self.assertIn(self.ticket_a_unassigned, tickets)
        self.assertIn(self.ticket_a_user_own, tickets)
        self.assertNotIn(self.ticket_a_user_team, tickets)
        self.assertNotIn(self.ticket_b_unassigned, tickets)
        self.assertIn(self.ticket_b_user_own, tickets)
        self.assertNotIn(self.ticket_b_user_team, tickets)

    @users("helpdesk_mgmt-user_team")
    def test_helpdesk_ticket_user_team(self):
        tickets = self.env["helpdesk.ticket"].search([])
        self.assertNotIn(self.ticket_a_unassigned, tickets)
        self.assertNotIn(self.ticket_a_user_own, tickets)
        self.assertIn(self.ticket_a_user_team, tickets)
        self.assertIn(self.ticket_b_unassigned, tickets)
        self.assertIn(self.ticket_b_user_own, tickets)
        self.assertIn(self.ticket_b_user_team, tickets)

    @users("helpdesk_mgmt-user")
    def test_helpdesk_ticket_user(self):
        tickets = self.env["helpdesk.ticket"].search([])
        self.assertIn(self.ticket_a_unassigned, tickets)
        self.assertIn(self.ticket_a_user_own, tickets)
        self.assertIn(self.ticket_a_user_team, tickets)
        self.assertIn(self.ticket_b_unassigned, tickets)
        self.assertIn(self.ticket_b_user_own, tickets)
        self.assertIn(self.ticket_b_user_team, tickets)

    def test_helpdesk_ticket_todo(self):
        self.assertEqual(
            self.team_a.todo_ticket_count,
            3,
            "Helpdesk Ticket: Helpdesk ticket team should have three tickets to do.",
        )
        self.assertEqual(
            self.team_a.todo_ticket_count_unassigned,
            1,
            "Helpdesk Ticket: Helpdesk ticket team should "
            "have one tickets unassigned.",
        )
        self.assertEqual(
            self.team_a.todo_ticket_count_high_priority,
            1,
            "Helpdesk Ticket: Helpdesk ticket team should "
            "have one ticket with high priority.",
        )
        self.assertEqual(
            self.team_a.todo_ticket_count_unattended,
            3,
            "Helpdesk Ticket: Helpdesk ticket team should "
            "have three tickets unattended.",
        )

        self.ticket_a_unassigned.write({"stage_id": self.stage_closed.id})
        self.assertEqual(
            self.team_a.todo_ticket_count_unattended,
            2,
            "Helpdesk Ticket: Helpdesk ticket team should "
            "have two tickets unattended.",
        )
        self.assertEqual(
            self.team_a.todo_ticket_count,
            2,
            "Helpdesk Ticket: Helpdesk ticket team should have two ticket to do.",
        )

    def test_dashboard_buttons(self):
        self.env["helpdesk.ticket"].search([]).write({"active": False})
        dashboard = self.env["helpdesk.ticket.team"]._retrieve_dashboard()
        self.assertEqual(dashboard[0]["value"], 0)
        self.assertEqual(dashboard[1]["value"], 0)
        ticket = self._create_ticket(self.env["helpdesk.ticket.team"])
        dashboard = self.env["helpdesk.ticket.team"]._retrieve_dashboard()
        self.assertEqual(dashboard[0]["value"], 1)
        self.assertEqual(dashboard[1]["value"], 1)
        ticket.team_id = self.team_a
        ticket.flush_recordset()
        dashboard = self.env["helpdesk.ticket.team"]._retrieve_dashboard()
        self.assertEqual(dashboard[0]["value"], 0)
        self.assertEqual(dashboard[1]["value"], 1)
