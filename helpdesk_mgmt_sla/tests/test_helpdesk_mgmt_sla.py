# Copyright (C) 2020 GARCO Consulting <www.garcoconsulting.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import timedelta

from freezegun import freeze_time

from odoo import Command, fields
from odoo.exceptions import AccessError, UserError

from odoo.addons.helpdesk_mgmt_sla.tests.common import CommonHelpdeskMgmtSla


class TestHelpdeskMgmtSla(CommonHelpdeskMgmtSla):
    @freeze_time(fields.Datetime.now() + timedelta(days=7))
    def test_sla_rule_global(self):
        """
        Test SLA rule without any filter, so it applies to all tickets
        """
        self.assertEqual(self.sla, self.ticket1.sla_ids)
        self.assertEqual(self.sla, self.ticket2.sla_ids)
        self.assertTrue(self.ticket1.sla_expired)
        self.assertTrue(self.ticket2.sla_expired)

    def test_sla_rule_team(self):
        """
        Test SLA rule filtered by team, so it applies only to tickets of that team
        """
        self.sla.team_ids = [Command.set([self.team1.id])]
        ticket1 = self.get_ticket(self.team1)
        ticket2 = self.get_ticket(self.team2)
        self.assertEqual(self.sla, ticket1.sla_ids)
        self.assertNotEqual(self.sla, ticket2.sla_ids)
        with freeze_time(fields.Datetime.now() + timedelta(hours=3)):
            self.assertTrue(ticket1.sla_expired)
            self.assertFalse(ticket2.sla_expired)

    def test_sla_rule_category(self):
        """
        Test SLA rule filtered by category, so it applies only to tickets of
        that category
        """
        self.sla.category_ids = [Command.set([self.category1.id])]
        ticket1 = self.get_ticket(self.team1, {"category_id": self.category1.id})
        ticket2 = self.get_ticket(self.team2, {"category_id": self.category2.id})
        self.assertEqual(self.sla, ticket1.sla_ids)
        self.assertNotEqual(self.sla, ticket2.sla_ids)
        with freeze_time(fields.Datetime.now() + timedelta(hours=3)):
            self.assertTrue(ticket1.sla_expired)
            self.assertFalse(ticket2.sla_expired)

    def test_sla_rule_tag(self):
        """
        Test SLA rule filtered by tag, so it applies only to tickets of that tag
        """
        self.sla.tag_ids = [Command.set([self.tag1.id])]
        ticket1 = self.get_ticket(self.team1, {"tag_ids": self.tag1})
        ticket2 = self.get_ticket(self.team2, {"tag_ids": self.tag2})
        self.assertEqual(self.sla, ticket1.sla_ids)
        self.assertNotEqual(self.sla, ticket2.sla_ids)
        with freeze_time(fields.Datetime.now() + timedelta(hours=3)):
            self.assertTrue(ticket1.sla_expired)
            self.assertFalse(ticket2.sla_expired)

    def test_sla_rule_domain(self):
        """
        Test SLA rule filtered by domain, so it applies only to tickets of that domain
        """
        self.sla.domain = f"[('tag_ids', '=', {self.tag1.id})]"
        ticket1 = self.get_ticket(self.team1, {"tag_ids": self.tag1})
        ticket2 = self.get_ticket(self.team2, {"tag_ids": self.tag2})
        self.assertEqual(self.sla, ticket1.sla_ids)
        self.assertNotEqual(self.sla, ticket2.sla_ids)
        with freeze_time(fields.Datetime.now() + timedelta(hours=3)):
            self.assertTrue(ticket1.sla_expired)
            self.assertFalse(ticket2.sla_expired)

    def test_sla_rule_change_stage(self):
        """
        Test SLA rule process when changing stages
        """
        ticket1 = self.get_ticket(self.team1)
        ticket2 = self.get_ticket(self.team2)
        self.assertEqual(self.sla, ticket1.sla_ids)
        self.assertEqual(self.sla, ticket2.sla_ids)
        with freeze_time(fields.Datetime.now() + timedelta(hours=1)):
            self.assertFalse(ticket1.sla_expired)
            self.assertFalse(ticket2.sla_expired)
            ticket1.write({"stage_id": self.stage2.id})
        ticket1.invalidate_recordset()
        ticket2.invalidate_recordset()
        self.assertFalse(ticket1.sla_deadline)
        self.assertTrue(ticket2.sla_deadline)
        ticket1.invalidate_recordset()
        ticket2.invalidate_recordset()
        with freeze_time(fields.Datetime.now() + timedelta(hours=3)):
            self.assertFalse(ticket1.sla_expired)
            self.assertTrue(ticket2.sla_expired)
            ticket2.write({"stage_id": self.stage2.id})
        ticket2.invalidate_recordset()
        self.assertTrue(ticket2.sla_expired)

    def test_sla_on_intermediate_stage(self):
        """
        Test SLA rule process when changing stages with a goal on an intermediate stage
        (not last)
        """
        self.sla.stage_id = self.stage1_2
        ticket1 = self.get_ticket(self.team1)
        self.assertEqual(self.sla, ticket1.sla_ids)
        with freeze_time(fields.Datetime.now() + timedelta(hours=1)):
            self.assertFalse(ticket1.sla_expired)
            ticket1.write({"stage_id": self.stage1_2.id})
        with freeze_time(fields.Datetime.now() + timedelta(hours=3)):
            ticket1.invalidate_recordset()
            self.assertFalse(ticket1.sla_expired)
            ticket1.write({"stage_id": self.stage2.id})
            self.assertFalse(ticket1.sla_expired)

    def test_sla_accomplished_on_create(self):
        """
        Test SLA rule process when created SLA on a done stage.
        It might be relevant when refreshing SLAs on existing tickets
        """
        self.ticket1.write({"stage_id": self.stage1_2.id})
        sla = self.env["helpdesk.sla"].create(
            {
                "name": "SLA on done stage",
                "days": 0,
                "hours": 2,
                "stage_id": self.stage1_1.id,
            }
        )
        self.ticket1.refresh_sla()
        self.assertEqual(
            self.ticket1.ticket_sla_ids.filtered(lambda r: r.sla_id == sla).state,
            "accomplished",
        )

    def test_sla_start_on_hold(self):
        """
        Test SLA rule process when starting on a on hold stage
        """
        self.sla.ignore_stage_ids = self.stage1
        ticket = self.get_ticket(self.team1, {"stage_id": self.stage1.id})
        self.assertEqual(ticket.ticket_sla_ids.state, "on_hold")

    def test_sla_create_permission(self):
        """
        Test that a user with only create permission on SLA can create tickets
        """
        ticket1 = (
            self.env["helpdesk.ticket"]
            .with_user(self.user_sla)
            .create(
                {
                    "name": "Test ticket",
                    "team_id": self.team1.id,
                    "description": "Test description",
                    "user_id": self.user_sla.id,
                }
            )
        )
        self.assertEqual(self.sla, ticket1.sla_ids)
        self.assertEqual(ticket1.create_uid, self.user_sla)

    def test_sla_write_permission(self):
        """
        Test that a user with only write permission on SLA can write SLA information
        """
        ticket1 = self.get_ticket(self.team1, {"user_id": self.user_sla.id})
        self.assertFalse(
            self.env["helpdesk.ticket.sla"]
            .with_user(self.user_sla)
            .search([("ticket_id", "=", ticket1.id)])
            .check_access("write")
        )

    def test_sla_no_write_permission(self):
        """
        Test that a user without write permission on SLA cannot edit SLA information
        """
        ticket1 = self.get_ticket(self.team1, {"user_id": self.env.user.id})
        self.assertFalse(
            self.env["helpdesk.ticket"]
            .with_user(self.user_sla)
            .search([("id", "=", ticket1.id)])
        )
        with self.assertRaises(AccessError):
            self.env["helpdesk.ticket.sla"].with_user(self.user_sla).search(
                [("ticket_id", "=", ticket1.id)]
            ).check_access("write")

    def test_colors(self):
        """
        Test SLA colors depending on the state of the SLA
        """
        self.sla.ignore_stage_ids = self.stage1_1
        ticket1 = self.get_ticket(self.team1)
        ticket2 = self.get_ticket(self.team1)
        sla_ticket1 = ticket1.ticket_sla_ids
        sla_ticket2 = ticket2.ticket_sla_ids
        self.assertEqual(sla_ticket1.color, 3)
        self.assertEqual(sla_ticket2.color, 3)
        ticket1.write({"stage_id": self.stage1_1.id})
        self.assertEqual(sla_ticket1.color, 0)
        ticket1.write({"stage_id": self.stage1_2.id})
        self.assertEqual(sla_ticket1.color, 3)
        ticket1.write({"stage_id": self.stage2.id})
        self.assertEqual(sla_ticket1.color, 10)
        with freeze_time(fields.Datetime.now() + timedelta(hours=3)):
            sla_ticket2.invalidate_recordset()
            self.assertEqual(sla_ticket2.color, 1)
            ticket2.write({"stage_id": self.stage2.id})
            self.assertEqual(sla_ticket2.color, 1)

    def test_sla_on_hold(self):
        """
        Test SLA on hold behavior
        """
        self.sla.ignore_stage_ids = self.stage1_1
        ticket1 = self.get_ticket(self.team1)
        with freeze_time(fields.Datetime.now() + timedelta(hours=1)):
            self.assertFalse(ticket1.sla_expired)
            ticket1.write({"stage_id": self.stage1_1.id})
        ticket1.invalidate_recordset()
        self.assertFalse(ticket1.sla_deadline)
        with freeze_time(fields.Datetime.now() + timedelta(hours=3)):
            self.assertFalse(ticket1.sla_expired)
            ticket1.write({"stage_id": self.stage1_2.id})
        ticket1.invalidate_recordset()
        self.assertTrue(ticket1.sla_deadline)
        with freeze_time(fields.Datetime.now() + timedelta(hours=3.5)):
            self.assertFalse(ticket1.sla_expired)
        ticket1.invalidate_recordset()
        with freeze_time(fields.Datetime.now() + timedelta(hours=5)):
            self.assertTrue(ticket1.sla_expired)

    def test_return_to_progress(self):
        self.ticket1.write({"stage_id": self.stage2.id})
        self.assertEqual(self.ticket1.ticket_sla_ids.state, "accomplished")
        self.ticket1.write({"stage_id": self.stage1.id})
        self.assertEqual(self.ticket1.ticket_sla_ids.state, "in_progress")

    def test_failed_return(self):
        """
        Test that once an SLA is expired, it remains expired even if the ticket
        goes back to a previous stage
        """
        self.sla.ignore_stage_ids = self.stage1_1
        ticket1 = self.get_ticket(self.team1)
        self.assertFalse(ticket1.ticket_sla_ids.expired)
        self.assertEqual(
            ticket1,
            self.env["helpdesk.ticket"].search(
                [("sla_expired", "=", False), ("id", "=", ticket1.id)]
            ),
        )
        self.assertFalse(
            self.env["helpdesk.ticket"].search(
                [("sla_expired", "=", True), ("id", "=", ticket1.id)]
            )
        )
        self.assertFalse(ticket1.sla_expired)
        self.assertFalse(ticket1.ticket_sla_ids.expired)
        ticket1.invalidate_recordset()
        ticket1.ticket_sla_ids.invalidate_recordset()
        with freeze_time(fields.Datetime.now() + timedelta(hours=3)):
            self.assertTrue(ticket1.sla_expired)
            self.assertTrue(ticket1.ticket_sla_ids.expired)
            self.assertEqual(
                ticket1,
                self.env["helpdesk.ticket"].search(
                    [("sla_expired", "=", True), ("id", "=", ticket1.id)]
                ),
            )
            self.assertFalse(
                self.env["helpdesk.ticket"].search(
                    [("sla_expired", "=", False), ("id", "=", ticket1.id)]
                )
            )
            ticket1.write({"stage_id": self.stage2.id})
            ticket1.invalidate_recordset()
            self.assertEqual(ticket1.ticket_sla_ids.state, "expired")
            self.assertTrue(ticket1.ticket_sla_ids.expired)
            self.assertEqual(
                ticket1,
                self.env["helpdesk.ticket"].search(
                    [("sla_expired", "=", True), ("id", "=", ticket1.id)]
                ),
            )
            self.assertFalse(
                self.env["helpdesk.ticket"].search(
                    [("sla_expired", "=", False), ("id", "=", ticket1.id)]
                )
            )
            ticket1.write({"stage_id": self.stage1_1.id})
            ticket1.invalidate_recordset()
            self.assertEqual(ticket1.ticket_sla_ids.state, "expired")
            ticket1.write({"stage_id": self.stage1.id})
            ticket1.invalidate_recordset()
            self.assertEqual(ticket1.ticket_sla_ids.state, "expired")

    def test_report(self):
        """
        Test SLA report generation and SQL queue
        """
        self.assertEqual(
            self.env["helpdesk.sla.report"]
            .search([("ticket_id", "=", self.ticket1.id)], limit=1)
            .state,
            "on_going",
        )

    def test_refresh_sla(self):
        # Test deletion of no longer applicable SLAs
        self.assertTrue(self.ticket1.sla_fits)
        self.sla.team_ids = [Command.set([self.team2.id])]
        self.ticket1.invalidate_recordset()
        self.assertFalse(self.ticket1.sla_fits)
        self.ticket1.refresh_sla()
        self.ticket1.invalidate_recordset()
        self.assertTrue(self.ticket1.sla_fits)
        self.assertFalse(self.ticket1.ticket_sla_ids)
        # Test addition of new applicable SLAs
        self.sla.team_ids = [Command.clear()]
        self.ticket1.invalidate_recordset()
        self.assertFalse(self.ticket1.sla_fits)
        self.ticket1.refresh_sla()
        self.ticket1.invalidate_recordset()
        self.assertTrue(self.ticket1.sla_fits)
        self.assertEqual(self.sla, self.ticket1.sla_ids)
        # Test no changes if SLAs still applicable, but other added
        sla = self.env["helpdesk.sla"].create(
            {
                "name": "New SLA",
                "days": 0,
                "hours": 2,
                "stage_id": self.stage2.id,
            }
        )
        self.ticket1.invalidate_recordset()
        self.assertFalse(self.ticket1.sla_fits)
        ticket_sla = self.ticket1.ticket_sla_ids
        self.ticket1.refresh_sla()
        self.ticket1.invalidate_recordset()
        self.assertEqual(
            ticket_sla,
            self.ticket1.ticket_sla_ids.filtered(lambda r: r.sla_id == self.sla),
        )
        self.assertTrue(self.ticket1.ticket_sla_ids.filtered(lambda r: r.sla_id == sla))

    def test_failed_query(self):
        with self.assertRaises(UserError):
            self.env["helpdesk.ticket.sla"].search([("expired", ">", True)])
