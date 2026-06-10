# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import datetime

from odoo import fields
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
            "Helpdesk Ticket: Helpdesk ticket team should have one tickets unassigned.",
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
            "Helpdesk Ticket: Helpdesk ticket team should have two tickets unattended.",
        )
        self.assertEqual(
            self.team_a.todo_ticket_count,
            2,
            "Helpdesk Ticket: Helpdesk ticket team should have two ticket to do.",
        )

    def test_fetch_agent_overview(self):
        self.env["helpdesk.ticket"].search([]).write({"active": False})
        overview = self.env["helpdesk.ticket.team"].fetch_agent_overview()
        self.assertTrue(overview["sample_mode"])
        self.assertEqual(overview["assigned_open"]["any"]["ticket_count"], 7)

        self._create_ticket(self.team_a, self.user)
        overview = (
            self.env["helpdesk.ticket.team"].with_user(self.user).fetch_agent_overview()
        )
        self.assertFalse(overview["sample_mode"])
        self.assertEqual(overview["assigned_open"]["any"]["ticket_count"], 1)
        self.assertGreaterEqual(overview["assigned_open"]["any"]["mean_open_hours"], 0)

    def test_fetch_agent_overview_priority_buckets(self):
        self.env["helpdesk.ticket"].search([]).write({"active": False})
        self._create_ticket(self.team_a, self.user)
        high = self._create_ticket(self.team_a, self.user)
        high.priority = "2"
        urgent = self._create_ticket(self.team_a, self.user)
        urgent.priority = "3"
        overview = (
            self.env["helpdesk.ticket.team"].with_user(self.user).fetch_agent_overview()
        )
        self.assertEqual(overview["assigned_open"]["high"]["ticket_count"], 1)
        self.assertEqual(overview["assigned_open"]["urgent"]["ticket_count"], 1)
        self.assertGreaterEqual(overview["assigned_closed"]["today"], 0)
        self.assertGreaterEqual(overview["assigned_closed"]["last_7_days"], 0)

    def test_overview_team_metrics(self):
        self.assertEqual(self.team_a.open_ticket_count, 3)
        self.assertEqual(self.team_a.unassigned_tickets, 1)
        self.assertEqual(self.team_a.urgent_ticket, 1)
        self.ticket_a_unassigned.write({"stage_id": self.stage_closed.id})
        self.assertEqual(self.team_a.open_ticket_count, 2)
        self.assertEqual(self.team_a.urgent_ticket, 0)

    def test_compute_ticket_closed_last_7_days(self):
        ticket = self._create_ticket(self.team_a, self.user)
        ticket.write(
            {
                "stage_id": self.stage_closed.id,
                "closed_date": fields.Datetime.now(),
            }
        )
        self.team_a.invalidate_recordset()
        self.assertEqual(self.team_a.ticket_closed, 1)

    def test_action_overview_team_open_tickets(self):
        action = self.team_a.action_overview_team_open_tickets()
        self.assertEqual(action["domain"], [("team_id", "in", self.team_a.ids)])
        self.assertEqual(action["context"]["default_team_id"], self.team_a.id)
        self.assertEqual(action["context"]["search_default_open"], 1)

    def test_action_overview_open_team_tickets(self):
        action = self.team_a.action_overview_open_team_tickets()
        self.assertEqual(action["domain"], [("team_id", "in", self.team_a.ids)])
        self.assertEqual(action["context"]["search_default_open"], 1)

    def test_action_overview_team_closed_week(self):
        action = self.team_a.action_overview_team_closed_week()
        self.assertEqual(action["domain"][0], ("team_id", "in", self.team_a.ids))
        self.assertEqual(action["domain"][1], ("closed", "=", True))
        self.assertEqual(action["context"]["search_default_closed_last_7_days"], 1)
        self.assertEqual(action["context"]["search_default_open"], 0)

    def test_action_overview_team_urgent_tickets(self):
        action = self.team_a.action_overview_team_urgent_tickets()
        self.assertEqual(action["context"]["search_default_urgent_priority"], 1)
        self.assertEqual(action["context"]["search_default_open"], 1)

    def test_ticket_open_hours(self):
        ticket = self._create_ticket(self.team_a, self.user)
        reference = ticket.create_date + datetime.timedelta(hours=5)
        self.assertAlmostEqual(ticket._elapsed_hours_until(reference), 5.0, places=1)
        ticket.write({"stage_id": self.stage_closed.id})
        self.assertTrue(ticket.closed)
        self.assertAlmostEqual(
            ticket.open_hours,
            ticket._elapsed_hours_until(ticket.closed_date),
            places=2,
        )

    def test_action_open_from_xmlid_merges_search_defaults(self):
        ticket_model = self.env["helpdesk.ticket"].with_context(
            search_default_open=1,
            search_default_mytickets=1,
            search_default_urgent_priority=1,
        )
        action = ticket_model.action_open_from_xmlid(
            "helpdesk_mgmt.overview_agent_open_tickets_window"
        )
        self.assertEqual(action["context"]["search_default_open"], 1)
        self.assertEqual(action["context"]["search_default_mytickets"], 1)
        self.assertEqual(action["context"]["search_default_urgent_priority"], 1)

    def test_action_open_from_xmlid_custom_title_and_search_view(self):
        action = self.env["helpdesk.ticket"].action_open_from_xmlid(
            "helpdesk_mgmt.overview_agent_open_tickets_window",
            title="Custom Overview",
            search_view_ref="helpdesk_mgmt.helpdesk_ticket_view_search",
        )
        self.assertEqual(action["display_name"], "Custom Overview")
        self.assertEqual(
            action["search_view_id"],
            self.env.ref("helpdesk_mgmt.helpdesk_ticket_view_search").id,
        )
