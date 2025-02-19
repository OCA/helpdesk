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
