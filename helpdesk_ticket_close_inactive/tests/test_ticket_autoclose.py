# Copyright 2024 APSL-Nagarro - Miquel Alzanillas
from datetime import datetime, timedelta

from odoo.tests import TransactionCase


class TestHelpdeskTicketAutoclose(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.team = cls.env["helpdesk.ticket.team"].create(
            {
                "name": "Test Team",
                "close_inactive_tickets": True,
                "inactive_tickets_day_limit_warning": 7,
                "inactive_tickets_day_limit_closing": 14,
            }
        )
        cls.stage_warning = cls.env["helpdesk.ticket.stage"].create(
            {"name": "Stage Warning"}
        )
        cls.stage_closing = cls.env["helpdesk.ticket.stage"].create(
            {"name": "Stage Closing"}
        )
        cls.type_warning = cls.env["helpdesk.ticket.category"].create(
            {"name": "Category Warning"}
        )
        cls.team.ticket_stage_ids = [(4, cls.stage_warning.id)]
        cls.team.ticket_category_ids = [(4, cls.type_warning.id)]
        cls.team.closing_ticket_stage = cls.stage_closing
        cls.remaining_days = (
            cls.team.inactive_tickets_day_limit_closing
            - cls.team.inactive_tickets_day_limit_warning
        )
        cls.ticket = cls.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "team_id": cls.team.id,
                "stage_id": cls.stage_warning.id,
                "category_id": cls.type_warning.id,
                "description": "Please help me",
                "last_stage_update": datetime.today() - timedelta(days=7),
            }
        )

        cls.team_without_category = cls.env["helpdesk.ticket.team"].create(
            {
                "name": "Test Team",
                "close_inactive_tickets": True,
                "inactive_tickets_day_limit_warning": 7,
                "inactive_tickets_day_limit_closing": 14,
            }
        )
        cls.team_without_category.ticket_stage_ids = [(4, cls.stage_warning.id)]
        cls.team_without_category.closing_ticket_stage = cls.stage_closing
        cls.remaining_days = (
            cls.team_without_category.inactive_tickets_day_limit_closing
            - cls.team_without_category.inactive_tickets_day_limit_warning
        )
        cls.ticket2 = cls.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket  Without Category",
                "team_id": cls.team_without_category.id,
                "stage_id": cls.stage_warning.id,
                "category_id": cls.type_warning.id,
                "description": "Please help me without category",
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
        """Test that the correct remaining days are set in the
        context for the warning email."""
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

    def test_close_tickets_without_category(self):
        """Test that tickets without category are closed."""
        self.ticket2.write({"last_stage_update": datetime.today() - timedelta(days=15)})
        self.team_without_category.close_team_inactive_tickets()
        self.assertEqual(
            self.ticket2.stage_id,
            self.stage_closing,
            "Ticket should be moved to the closing stage",
        )
