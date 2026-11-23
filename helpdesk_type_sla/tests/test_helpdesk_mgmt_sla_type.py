# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import timedelta

from freezegun import freeze_time

from odoo import Command, fields

from odoo.addons.helpdesk_mgmt_sla.tests.common import CommonHelpdeskMgmtSla


class TestHelpDeskRule(CommonHelpdeskMgmtSla):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.type1 = cls.env["helpdesk.ticket.type"].create({"name": "Type One"})
        cls.type2 = cls.env["helpdesk.ticket.type"].create({"name": "Type Two"})

    def test_sla_rule_type(self):
        self.sla.type_ids = [Command.set([self.type1.id])]
        ticket1 = self.get_ticket(self.team1, {"type_id": self.type1.id})
        ticket2 = self.get_ticket(self.team2, {"type_id": self.type2.id})
        with freeze_time(fields.Datetime.now() + timedelta(days=7)):
            self.assertTrue(ticket1.sla_expired)
            self.assertFalse(ticket2.sla_expired)

    def test_sla_rule_no_type(self):
        ticket1 = self.get_ticket(self.team1, {"type_id": self.type1.id})
        ticket2 = self.get_ticket(self.team2, {"type_id": self.type2.id})
        with freeze_time(fields.Datetime.now() + timedelta(days=7)):
            self.assertTrue(ticket1.sla_expired)
            self.assertTrue(ticket2.sla_expired)

    def test_restricted_sla_excludes_untyped_ticket(self):
        self.sla.type_ids = [Command.set(self.type1.ids)]
        ticket = self.get_ticket(self.team1, {"type_id": False})
        self.assertFalse(ticket.type_id)
        self.assertNotIn(self.sla, ticket.sla_ids)

    def test_unrestricted_sla_includes_untyped_ticket(self):
        self.sla.type_ids = [Command.clear()]
        ticket = self.get_ticket(self.team1, {"type_id": False})
        self.assertFalse(ticket.type_id)
        self.assertIn(self.sla, ticket.sla_ids)

    def test_type_filter_preserves_team_restriction(self):
        self.sla.team_ids = [Command.set(self.team1.ids)]
        for type_ids in [self.type1.ids, []]:
            self.sla.type_ids = [Command.set(type_ids)]
            for team, applies in [(self.team1, True), (self.team2, False)]:
                with self.subTest(rule_types=type_ids, team=team.id):
                    ticket = self.get_ticket(team, {"type_id": self.type1.id})
                    self.assertEqual(self.sla in ticket.sla_ids, applies)

    def test_type_filter_preserves_tag_restriction(self):
        self.sla.tag_ids = [Command.set(self.tag1.ids)]
        for type_ids in [self.type1.ids, []]:
            self.sla.type_ids = [Command.set(type_ids)]
            for tag_ids, applies in [
                (self.tag1.ids, True),
                (self.tag2.ids, False),
                ([], False),
            ]:
                with self.subTest(rule_types=type_ids, tags=tag_ids):
                    ticket = self.get_ticket(
                        self.team1,
                        {
                            "type_id": self.type1.id,
                            "tag_ids": [Command.set(tag_ids)],
                        },
                    )
                    self.assertEqual(self.sla in ticket.sla_ids, applies)

    def test_type_filter_preserves_category_restriction(self):
        self.sla.category_ids = [Command.set(self.category1.ids)]
        for type_ids in [self.type1.ids, []]:
            self.sla.type_ids = [Command.set(type_ids)]
            for category_id, applies in [
                (self.category1.id, True),
                (self.category2.id, False),
                (False, False),
            ]:
                with self.subTest(rule_types=type_ids, category=category_id):
                    ticket = self.get_ticket(
                        self.team1,
                        {"type_id": self.type1.id, "category_id": category_id},
                    )
                    self.assertEqual(self.sla in ticket.sla_ids, applies)

    def test_batch_type_filter_as_helpdesk_user(self):
        self.user_sla.group_ids = [
            Command.link(self.env.ref("helpdesk_mgmt.group_helpdesk_user").id)
        ]
        self.assertFalse(
            self.user_sla.has_group("helpdesk_mgmt.group_helpdesk_manager")
        )
        self.sla.write(
            {
                "type_ids": [Command.set(self.type1.ids)],
                "team_ids": [Command.set(self.team1.ids)],
            }
        )
        tickets = (
            self.env["helpdesk.ticket"]
            .with_user(self.user_sla)
            .create(
                [
                    {
                        "name": "Type filtering batch ticket",
                        "description": "SLA type filtering regression",
                        "team_id": team.id,
                        "type_id": type_id,
                        "user_id": self.user_sla.id,
                    }
                    for team, type_id in [
                        (self.team1, self.type1.id),
                        (self.team1, self.type2.id),
                        (self.team1, False),
                        (self.team2, self.type1.id),
                    ]
                ]
            )
        )
        self.assertEqual(tickets.mapped("create_uid"), self.user_sla)
        self.assertEqual(
            [self.sla in ticket.sla_ids for ticket in tickets],
            [True, False, False, False],
        )
