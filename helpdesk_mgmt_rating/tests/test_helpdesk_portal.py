# Copyright 2024 Tecnativa - Carolina Fernandez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo.addons.base.tests.common import HttpCaseWithUserPortal


class TestHelpdeskPortalBase(HttpCaseWithUserPortal):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {"name": "Test partner", "email": "test@email.com"}
        )
        cls.stage_done = cls.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_done")
        cls.stage_done.rating_mail_template_id = cls.env.ref(
            "helpdesk_mgmt_rating.rating_ticket_email_template"
        )
        cls.ticket = cls.env["helpdesk.ticket"].create(
            {
                "name": "Test 1",
                "description": "Ticket test",
                "partner_id": cls.partner.id,
                "stage_id": cls.stage_done.id,
            }
        )

    def test_rating_satisfied_ticket(self):
        """Rate satisfied ticket from the portal."""
        self.authenticate("portal", "portal")
        portal_access_token = self.ticket._rating_get_access_token()
        resp = self.url_open(f"/rate/{portal_access_token}/5")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.ticket.positive_rate_percentage, 100)

    def test_rating_not_satisfied_ticket(self):
        """Rate not satisfied ticket from the portal."""
        self.authenticate("portal", "portal")
        portal_access_token = self.ticket._rating_get_access_token()
        resp = self.url_open(f"/rate/{portal_access_token}/3")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.ticket.positive_rate_percentage, 0)

    def test_rating_dissatisfied_ticket(self):
        """Rate highly dissatisfied ticket from the portal."""
        self.authenticate("portal", "portal")
        portal_access_token = self.ticket._rating_get_access_token()
        resp = self.url_open(f"/rate/{portal_access_token}/1")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.ticket.positive_rate_percentage, 0)
