# Copyright 2024 APSL-Nagarro - Miquel Alzanillas
from datetime import datetime, timedelta

from odoo.addons.base.tests.common import BaseCommon


class TestHelpdeskTicketAutoclose(BaseCommon):
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.team = self.env["helpdesk.ticket.team"].create(
            {
                "name": "Test Team",
                "close_inactive_tickets": True,
                "inactive_tickets_day_limit_warning": 7,
                "inactive_tickets_day_limit_closing": 14,
            }
        )
        self.stage_warning = self.env["helpdesk.ticket.stage"].create(
            {"name": "Stage Warning"}
        )
        self.stage_closing = self.env["helpdesk.ticket.stage"].create(
            {"name": "Stage Closing"}
        )
        self.type_warning = self.env["helpdesk.ticket.category"].create(
            {"name": "Category Warning"}
        )
        self.team.ticket_stage_ids = [(4, self.stage_warning.id)]
        self.team.ticket_category_ids = [(4, self.type_warning.id)]
        self.team.closing_ticket_stage = self.stage_closing
        self.remaining_days = (
            self.team.inactive_tickets_day_limit_closing
            - self.team.inactive_tickets_day_limit_warning
        )
        self.ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "team_id": self.team.id,
                "stage_id": self.stage_warning.id,
                "category_id": self.type_warning.id,
                "description": "Please help me",
                "last_stage_update": datetime.today() - timedelta(days=7),
            }
        )

    def test_warning_email_sent(self):
        """Test that a warning email is sent after the warning day limit is reached."""
        self.ticket.write({"last_stage_update": datetime.today() - timedelta(days=7)})
        result = self.team.close_team_inactive_tickets()
        sent_mails = self.env["mail.mail"].search(
            [("id", "in", result["warning_email_ids"])]
        )
        self.assertTrue(sent_mails, "Warning email have been sent")

    def test_stage_filter_uses_original_relation(self):
        self.assertEqual(
            self.team._fields["ticket_stage_ids"].relation,
            "helpdesk_team_stage_closing_ticket_filter_rel",
        )

    def test_stage_assignment_does_not_change_closure_filter(self):
        self.stage_closing.write({"team_ids": [(4, self.team.id)]})
        self.team.invalidate_recordset(["ticket_stage_ids"])
        self.assertEqual(self.team.ticket_stage_ids, self.stage_warning)

    def test_adding_filter_stage_does_not_assign_team(self):
        self.team.write({"ticket_stage_ids": [(4, self.stage_closing.id)]})
        self.stage_closing.invalidate_recordset(["team_ids"])
        self.assertFalse(self.stage_closing.team_ids)

    def test_removing_filter_stage_preserves_team_assignment(self):
        self.stage_warning.write({"team_ids": [(4, self.team.id)]})
        self.team.write({"ticket_stage_ids": [(3, self.stage_warning.id)]})
        self.stage_warning.invalidate_recordset(["team_ids"])
        self.assertEqual(self.stage_warning.team_ids, self.team)

    def test_closed_ticket_is_not_closed_again(self):
        self.stage_closing.closed = True
        self.team.write({"ticket_stage_ids": [(4, self.stage_closing.id)]})
        self.ticket.write({"stage_id": self.stage_closing.id})
        old_date = datetime.today() - timedelta(days=30)
        self.ticket.write({"last_stage_update": old_date, "closed_date": old_date})
        messages = self.ticket.message_ids
        result = self.team.close_team_inactive_tickets()
        self.assertEqual(self.ticket.closed_date, old_date)
        self.assertEqual(self.ticket.last_stage_update, old_date)
        self.assertEqual(self.ticket.message_ids, messages)
        self.assertFalse(result["closing_email_ids"])

    def test_closed_ticket_does_not_receive_warning(self):
        self.stage_closing.closed = True
        self.team.write({"ticket_stage_ids": [(4, self.stage_closing.id)]})
        self.ticket.write({"stage_id": self.stage_closing.id})
        self.ticket.write({"last_stage_update": datetime.today() - timedelta(days=7)})
        result = self.team.close_team_inactive_tickets()
        self.assertFalse(result["warning_email_ids"])

    def test_ticket_closing_after_closing_day_limit(self):
        """Test that a ticket is closed after the closing day limit is reached."""
        self.ticket.write({"last_stage_update": datetime.today() - timedelta(days=15)})
        self.team.close_team_inactive_tickets()
        self.assertEqual(
            self.ticket.stage_id,
            self.stage_closing,
            "Ticket should be moved to the closing stage",
        )

    def test_closing_email_sent(self):
        """Test that a closing email is sent when the ticket is closed automatically."""
        self.ticket.write({"last_stage_update": datetime.today() - timedelta(days=15)})
        result = self.team.close_team_inactive_tickets()
        sent_mails = self.env["mail.mail"].search(
            [("id", "in", result["closing_email_ids"])]
        )
        self.assertTrue(sent_mails, "Closing email should have been sent")

    def test_remaining_days_in_context(self):
        """Test that the correct remaining days are
        set in the context for the warning email."""
        self.ticket.write({"last_stage_update": datetime.today() - timedelta(days=7)})
        result = self.team.close_team_inactive_tickets()
        sent_mail = self.env["mail.mail"].search(
            [("id", "in", result["warning_email_ids"])], limit=1
        )
        self.assertIn(
            str(self.remaining_days) + " days",
            sent_mail.body_html,
            "The warning email should contain the remaining "
            "days until the ticket is closed.",
        )

    def test_warning_phase_disabled_when_days_zero(self):
        """Test that no warning email is sent when the warning day limit is 0."""
        self.team.write({"inactive_tickets_day_limit_warning": 0})
        self.ticket.write({"last_stage_update": datetime.today() - timedelta(days=7)})
        result = self.team.close_team_inactive_tickets()
        self.assertFalse(
            result["warning_email_ids"],
            "No warning email should be sent when the warning day limit is 0.",
        )
        self.assertEqual(
            self.ticket.stage_id,
            self.stage_warning,
            "Ticket should not be closed when it has not reached the closing limit.",
        )

    def test_closing_email_not_sent_when_no_template(self):
        """Test that the ticket is closed but no closing email is sent
        when the closing email template is not set."""
        self.team.write({"close_inactive_mail_template_id": False})
        self.ticket.write({"last_stage_update": datetime.today() - timedelta(days=15)})
        result = self.team.close_team_inactive_tickets()
        self.assertEqual(
            self.ticket.stage_id,
            self.stage_closing,
            "Ticket should still be moved to the closing stage.",
        )
        self.assertFalse(
            result["closing_email_ids"],
            "No closing email should be sent when the template is not set.",
        )

    def test_closing_applies_to_all_categories_when_none_selected(self):
        """Test that tickets of all categories are closed when no category
        filter is set on the team."""
        self.team.write({"ticket_category_ids": [(5, 0, 0)]})
        ticket_no_category = self.env["helpdesk.ticket"].create(
            {
                "name": "Ticket Without Category",
                "team_id": self.team.id,
                "stage_id": self.stage_warning.id,
                "description": "Please help me",
                "last_stage_update": datetime.today() - timedelta(days=15),
            }
        )
        self.ticket.write({"last_stage_update": datetime.today() - timedelta(days=15)})
        self.team.close_team_inactive_tickets()
        self.assertEqual(
            self.ticket.stage_id,
            self.stage_closing,
            "Ticket with a category should be closed when no category filter is set.",
        )
        self.assertEqual(
            ticket_no_category.stage_id,
            self.stage_closing,
            "Ticket without a category should also be closed "
            "when no category filter is set.",
        )
