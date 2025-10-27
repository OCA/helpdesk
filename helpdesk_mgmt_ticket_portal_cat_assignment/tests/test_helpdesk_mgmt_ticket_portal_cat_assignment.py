# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.fields import Command
from odoo.tests.common import new_test_user, tagged

from odoo.addons.base.tests.common import HttpCaseWithUserPortal


@tagged("default_partner")
class TestHelpdeskPortalUserAssignment(HttpCaseWithUserPortal):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.portal_user = new_test_user(
            cls.env,
            login="test_portal_user",
            groups="base.group_portal",
        )
        cls.default_user = cls.env["res.users"].create(
            {
                "name": "Default User",
                "login": "default_user",
                "email": "default@example.com",
                "groups_id": [
                    Command.set([cls.env.ref("helpdesk_mgmt.group_helpdesk_user").id])
                ],
            }
        )
        cls.category_with_default = cls.env["helpdesk.ticket.category"].create(
            {
                "name": "Category with Default Partner",
                "default_partner_id": cls.default_user.id,
            }
        )
        cls.category_without_default = cls.env["helpdesk.ticket.category"].create(
            {
                "name": "Category without default user",
            }
        )
        cls.team_leader_a = cls.env["res.users"].create(
            {
                "name": "Team Leader A",
                "login": "team_leader_a",
                "email": "leader_a@example.com",
                "groups_id": [
                    Command.set([cls.env.ref("helpdesk_mgmt.group_helpdesk_user").id])
                ],
            }
        )
        cls.team_a = cls.env["helpdesk.ticket.team"].create(
            {
                "name": "Support Team A",
                "user_id": cls.team_leader_a.id,
                "user_ids": [Command.set([cls.team_leader_a.id, cls.default_user.id])],
            }
        )
        cls.team_leader_b = cls.env["res.users"].create(
            {
                "name": "Team Leader B",
                "login": "team_leader_b",
                "email": "leader_b@example.com",
                "groups_id": [
                    Command.set([cls.env.ref("helpdesk_mgmt.group_helpdesk_user").id])
                ],
            }
        )
        cls.team_b = cls.env["helpdesk.ticket.team"].create(
            {
                "name": "Support Team B",
                "user_id": cls.team_leader_b.id,
                "user_ids": [Command.set([cls.team_leader_b.id])],
            }
        )

    def test_portal_with_category_default_assigns_default_user(self):
        ticket_with_default_user = (
            self.env["helpdesk.ticket"]
            .sudo()
            .with_user(self.portal_user)
            .create(
                {
                    "name": "Ticket with default user",
                    "category_id": self.category_with_default.id,
                    "description": "",
                }
            )
        )
        self.assertEqual(
            ticket_with_default_user.user_id,
            self.default_user,
            "Ticket should be assigned to the default user.",
        )

    def test_portal_without_category_default_assigns_portal_user(self):
        ticket_without_default_user = (
            self.env["helpdesk.ticket"]
            .sudo()
            .with_user(self.portal_user)
            .create(
                {
                    "name": "Ticket without default user",
                    "category_id": self.category_without_default.id,
                    "description": "",
                }
            )
        )
        self.assertEqual(
            ticket_without_default_user.user_id,
            self.portal_user,
            "Ticket should be assigned to the portal user.",
        )

    def test_internal_user_creates_ticket_assigns_internal_user(self):
        ticket_by_internal_user = (
            self.env["helpdesk.ticket"]
            .with_user(self.default_user)
            .create(
                {
                    "name": "Ticket by internal user",
                    "category_id": self.category_with_default.id,
                    "description": "",
                }
            )
        )
        self.assertEqual(
            ticket_by_internal_user.user_id,
            self.default_user,
            "Ticket should be assigned to the internal user.",
        )

    def test_portal_team_option_enabled_without_team_assigns_portal_user(self):
        self.env.company.helpdesk_mgmt_portal_select_team = True
        ticket_with_option_enabled = (
            self.env["helpdesk.ticket"]
            .sudo()
            .with_user(self.portal_user)
            .create(
                {
                    "name": "Ticket with portal team option enabled",
                    "category_id": self.category_with_default.id,
                    "description": "",
                }
            )
        )
        self.assertEqual(
            ticket_with_option_enabled.user_id,
            self.portal_user,
            "Ticket should be assigned to the portal user",
        )

    def test_portal_team_option_enabled_with_team_including_default_assigns_default(
        self
    ):
        self.env.company.helpdesk_mgmt_portal_select_team = True
        ticket_with_team_default_in = (
            self.env["helpdesk.ticket"]
            .sudo()
            .with_user(self.portal_user)
            .create(
                {
                    "name": "Ticket with team (default in team)",
                    "category_id": self.category_with_default.id,
                    "team_id": self.team_a.id,
                    "description": "",
                }
            )
        )
        self.assertEqual(
            ticket_with_team_default_in.user_id,
            self.default_user,
            "When portal team selection is enabled and category default user "
            "is in the team, ticket should be assigned to that default user.",
        )
