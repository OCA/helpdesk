# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.exceptions import ValidationError
from odoo.tests import common
from odoo.tests.common import tagged


@tagged("team_customer")
class TestHelpdeskTeamCustomer(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.Team = cls.env["helpdesk.ticket.team"]
        cls.Ticket = cls.env["helpdesk.ticket"]
        cls.Partner = cls.env["res.partner"]
        cls.team_a = cls.Team.create({"name": "Team A"})
        cls.default_partner = cls.Partner.create(
            {"name": "Default", "email": "d@example.com"}
        )
        cls.allowed_partner = cls.Partner.create(
            {"name": "Allowed", "email": "a@example.com"}
        )

    def test_partner_name_matches_partner(self):
        ticket = self.Ticket.new({"team_id": self.team_a.id})
        ticket.partner_id = self.default_partner
        ticket._onchange_partner_id()
        self.assertEqual(ticket.partner_id.id, self.default_partner.id)
        self.assertEqual(ticket.partner_name, self.default_partner.name)

    def test_unique_partner_is_false_when_default_partner_is_false(self):
        self.team_a.write(
            {
                "default_partner_id": self.default_partner.id,
                "is_unique_partner": True,
                "allowed_partner_ids": [(5, 0, 0)],
            }
        )
        self.team_a.write({"default_partner_id": False})
        self.team_a._onchange_default_partner_id()
        self.assertFalse(self.team_a.is_unique_partner)

    def test_partner_domain_with_unique_partner(self):
        self.team_a.write(
            {
                "default_partner_id": self.default_partner.id,
                "is_unique_partner": True,
                "allowed_partner_ids": [(5, 0, 0)],
            }
        )
        ticket = self.Ticket.new({"team_id": self.team_a.id})
        ticket._compute_partner_id_domain()
        self.assertEqual(
            ticket.partner_id_domain, [("id", "=", self.default_partner.id)]
        )

    def test_partner_domain_with_default_and_allowed_partners(self):
        self.team_a.write(
            {
                "default_partner_id": self.default_partner.id,
                "is_unique_partner": False,
                "allowed_partner_ids": [(6, 0, [self.allowed_partner.id])],
            }
        )
        ticket = self.Ticket.new({"team_id": self.team_a.id})
        ticket._compute_partner_id_domain()
        domain = ticket.partner_id_domain
        self.assertEqual(len(domain), 1)
        field, operator, ids = domain[0]
        self.assertEqual(field, "id")
        self.assertEqual(operator, "in")
        self.assertCountEqual(ids, [self.default_partner.id, self.allowed_partner.id])

    def test_partner_domain_with_default_no_allowed_partners(self):
        self.team_a.write(
            {
                "default_partner_id": self.default_partner.id,
                "is_unique_partner": False,
                "allowed_partner_ids": [(5, 0, 0)],
            }
        )
        ticket = self.Ticket.new({"team_id": self.team_a.id})
        ticket._compute_partner_id_domain()
        self.assertEqual(ticket.partner_id_domain, [])

    def test_partner_domain_without_default_partner(self):
        self.team_a.write(
            {
                "default_partner_id": False,
                "is_unique_partner": False,
                "allowed_partner_ids": [(6, 0, [self.allowed_partner.id])],
            }
        )
        ticket = self.Ticket.new({"team_id": self.team_a.id})
        ticket._compute_partner_id_domain()
        self.assertFalse(ticket.partner_id)
        domain = ticket.partner_id_domain
        self.assertEqual(len(domain), 1)
        field, operator, ids = domain[0]
        self.assertEqual(field, "id")
        self.assertEqual(operator, "in")
        self.assertCountEqual(ids, self.team_a.allowed_partner_ids.ids)

    def test_constraint_allows_default_and_allowed_partners(self):
        self.team_a.write(
            {
                "default_partner_id": self.default_partner.id,
                "is_unique_partner": False,
                "allowed_partner_ids": [(6, 0, [self.allowed_partner.id])],
            }
        )
        ticket_default = self.Ticket.create(
            {
                "team_id": self.team_a.id,
                "partner_id": self.default_partner.id,
                "name": "test default",
                "description": "test default",
            }
        )
        self.assertEqual(ticket_default.partner_id, self.default_partner)
        ticket_allowed = self.Ticket.create(
            {
                "team_id": self.team_a.id,
                "partner_id": self.allowed_partner.id,
                "name": "test allowed",
                "description": "test allowed",
            }
        )
        self.assertEqual(ticket_allowed.partner_id, self.allowed_partner)

    def test_constraint_raises_for_not_allowed_partner(self):
        self.team_a.write(
            {
                "default_partner_id": self.default_partner.id,
                "is_unique_partner": True,
                "allowed_partner_ids": [(5, 0, 0)],
            }
        )
        with self.assertRaises(ValidationError):
            self.Ticket.create(
                {
                    "team_id": self.team_a.id,
                    "partner_id": self.allowed_partner.id,
                    "name": "test not allowed",
                    "description": "test not allowed",
                }
            )
