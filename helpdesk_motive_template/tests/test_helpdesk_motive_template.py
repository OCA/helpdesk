# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.tools import is_html_empty


class TestHelpdeskMotiveTemplate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.team = cls.env["helpdesk.ticket.team"].create(
            {
                "name": "Customer Support",
            }
        )
        cls.motive_with_default = cls.env["helpdesk.ticket.motive"].create(
            {
                "name": "Test Motive",
                "team_id": cls.team.id,
                "description_template": (
                    "<p>This is a description for ticket {{ ticket.name }}.</p>"
                ),
            }
        )
        cls.motive_without_default = cls.env["helpdesk.ticket.motive"].create(
            {
                "name": "Test Motive without Description Template",
                "team_id": cls.team.id,
            }
        )

    def test_description_prefill_on_motive_change(self):
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "TICKET-001",
                "team_id": self.team.id,
                "description": "Test description",
            }
        )
        ticket.motive_id = self.motive_with_default
        self.assertFalse(is_html_empty(ticket.description))
        self.assertIn(
            "This is a description for ticket TICKET-001.", ticket.description
        )

    def test_default_description_empty_template(self):
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "TICKET-002",
                "team_id": self.team.id,
                "description": "Test description",
            }
        )
        ticket.motive_id = self.motive_without_default
        self.assertIn(
            "Test description",
            ticket.description,
            "The description should not change if no template on the motive",
        )
