# Copyright 2025 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.exceptions import ValidationError

from odoo.addons.base.tests.common import BaseCommon


class TestHelpdeskTicketAssign(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = cls.env["res.users"].create(
            {"name": "User 1", "login": "user1@example.com"}
        )
        cls.user2 = cls.env["res.users"].create(
            {"name": "User 2", "login": "user2@example.com"}
        )
        cls.user3 = cls.env["res.users"].create(
            {"name": "User 3", "login": "user3@example.com"}
        )
        cls.team = cls.env["helpdesk.ticket.team"].create(
            {
                "name": "Team",
                "user_ids": [Command.set([cls.user1.id, cls.user2.id, cls.user3.id])],
                "assign_method": "manual",
            }
        )

    def _create_ticket(self, **extra):
        vals = {
            "name": "Test Ticket",
            "description": "Test description",
            "team_id": self.team.id,
            **extra,
        }
        return self.env["helpdesk.ticket"].create(vals)

    def test_get_new_user_manual(self):
        self.team.assign_method = "manual"
        self.assertFalse(self.team.get_new_user())

    def test_get_new_user_randomly(self):
        self.team.assign_method = "randomly"
        self.assertIn(self.team.get_new_user(), self.team.user_ids)

    def test_get_new_user_balanced(self):
        self.team.assign_method = "balanced"
        self._create_ticket(user_id=self.user1.id)
        self._create_ticket(user_id=self.user2.id)
        self.assertEqual(self.team.get_new_user(), self.user3)

    def test_get_new_user_sequential(self):
        self.team.assign_method = "sequential"
        user1 = self.team.get_new_user()
        self._create_ticket(user_id=user1.id)
        user2 = self.team.get_new_user()
        self.assertIn(user2, self.team.user_ids)
        self.assertNotEqual(user1, user2)

    def test_assign_method_constraint(self):
        self.team.assign_method = "manual"
        self.team.user_ids = [Command.clear()]
        with self.assertRaises(ValidationError):
            self.team.assign_method = "randomly"

    def test_onchange_user_ids_sets_manual(self):
        self.team.assign_method = "randomly"
        with self.assertRaises(ValidationError):
            self.team.user_ids = [Command.clear()]

    def test_onchange_user_ids_sets_manual_when_cleared(self):
        self.team.assign_method = "randomly"
        self.assertEqual(self.team.assign_method, "randomly")
        team = self.team.new(self.team.read()[0])
        team.user_ids = [Command.clear()]
        team._onchange_user_ids()
        self.assertEqual(team.assign_method, "manual")

    def test_default_get_assigns_user(self):
        self.team.assign_method = "balanced"
        fields_list = ["team_id", "user_id"]
        vals = self.env["helpdesk.ticket"].default_get(fields_list)
        vals["team_id"] = self.team.id
        vals["name"] = "Test Ticket"
        vals["description"] = "Test description"
        ticket = self.env["helpdesk.ticket"].create(vals)
        self.assertTrue(ticket.user_id)
        self.assertIn(ticket.user_id, self.team.user_ids)

    def test_default_get_no_assignment_on_manual_team(self):
        self.team.assign_method = "manual"
        fields_list = ["team_id", "user_id"]
        vals = self.env["helpdesk.ticket"].default_get(fields_list)
        vals["team_id"] = self.team.id
        vals["name"] = "Test Ticket"
        vals["description"] = "Test description"
        ticket = self.env["helpdesk.ticket"].create(vals)
        self.assertFalse(ticket.user_id)

    def test_default_get_no_assignment_if_already_in_res(self):
        self.team.assign_method = "randomly"

        vals = self.env["helpdesk.ticket"].default_get(["team_id", "user_id"])

        vals["user_id"] = self.user1.id
        vals["team_id"] = self.team.id
        vals["name"] = "Test Ticket"
        vals["description"] = "Test description"

        ticket = self.env["helpdesk.ticket"].create(vals)
        self.assertEqual(ticket.user_id, self.user1)

    def test_onchange_team_id_assigns_user(self):
        self.team.assign_method = "randomly"

        ticket = self.env["helpdesk.ticket"].new(
            {
                "team_id": self.team.id,
                "name": "Test Ticket",
            }
        )

        ticket.user_id = False

        ticket._onchange_team_id()

        self.assertTrue(ticket.user_id)
        self.assertIn(ticket.user_id, self.team.user_ids)

    def test_onchange_team_id_no_assignment_if_user_already_set(self):
        self.team.assign_method = "randomly"

        ticket = self.env["helpdesk.ticket"].new(
            {
                "team_id": self.team.id,
                "name": "Test Ticket",
                "user_id": self.user1.id,
            }
        )

        ticket._onchange_team_id()

        self.assertEqual(ticket.user_id, self.user1)

    def test_onchange_team_id_no_assignment_on_manual_team(self):
        self.team.assign_method = "manual"

        ticket = self.env["helpdesk.ticket"].new(
            {
                "team_id": self.team.id,
                "name": "Test Ticket",
            }
        )
        ticket.user_id = False
        ticket._onchange_team_id()
        self.assertFalse(ticket.user_id)

    def test_ticket_create_assigns_user(self):
        self.team.assign_method = "randomly"
        ticket = self._create_ticket()
        self.assertIn(ticket.user_id, self.team.user_ids)

    def test_ticket_create_no_assignment_without_team(self):
        self.team.assign_method = "randomly"

        vals = {
            "name": "Test Ticket No Team",
            "description": "Test description",
            "team_id": False,
        }

        ticket = self.env["helpdesk.ticket"].create(vals)
        self.assertFalse(ticket.team_id)
        self.assertNotIn(ticket.user_id, self.team.user_ids)
