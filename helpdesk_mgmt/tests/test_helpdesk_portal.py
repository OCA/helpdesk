# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import odoo.tests
from odoo import http
from odoo.tests import new_test_user


@odoo.tests.tagged("post_install", "-at_install")
class TestHelpdeskPortal(odoo.tests.HttpCase):
    """Test controllers defined for portal mode.
    This is mostly for basic coverage; we don't go as far as fully validating
    HTML produced by our routes.
    """

    def setUp(self):
        super().setUp()
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        self.company = self.env.ref("base.main_company")
        self.basic_user = new_test_user(
            self.env, login="test-user", password="test-user", context=ctx
        )
        self.basic_user.parent_id = self.company.partner_id
        self.portal_user = new_test_user(
            self.env,
            login="test-portal",
            password="test-portal",
            groups="base.group_portal",
            context=ctx,
        )
        self.partner_portal = self.portal_user.partner_id
        self.partner_portal.parent_id = self.company.partner_id
        self.new_ticket_title = "portal-new-submitted-ticket-subject"
        self.new_ticket_desc_lines = (  # multiline description to check line breaks
            "portal-new-submitted-ticket-description-line-1",
            "portal-new-submitted-ticket-description-line-2",
        )
        # Create a ticket submitted by our portal user.
        self.portal_ticket = self._create_ticket(
            self.partner_portal, "portal-ticket-title"
        )

    def get_new_tickets(self, user):
        return self.env["helpdesk.ticket"].with_user(user).search([])

    def _create_ticket(self, partner, ticket_title):
        """Create a ticket submitted by the specified partner."""
        return self.env["helpdesk.ticket"].create(
            {
                "name": ticket_title,
                "description": "test-description",
                "partner_id": partner.id,
                "partner_email": partner.email,
                "partner_name": partner.name,
            }
        )

    def _submit_ticket(self):
        resp = self.url_open(
            "/submitted/ticket",
            data={
                "category": self.env.ref("helpdesk_mgmt.helpdesk_category_1").id,
                "csrf_token": http.WebRequest.csrf_token(self),
                "subject": self.new_ticket_title,
                "description": "\n".join(self.new_ticket_desc_lines),
            },
        )
        self.assertEqual(resp.status_code, 200)

    def test_submit_ticket_01(self):
        self.authenticate("test-user", "test-user")
        self._submit_ticket()
        tickets = self.get_new_tickets(self.basic_user)
        self.assertNotIn(self.portal_ticket, tickets)
        self.assertIn(self.new_ticket_title, tickets.mapped("name"))

    def test_submit_ticket_02(self):
        self.authenticate("test-portal", "test-portal")
        self._submit_ticket()
        tickets = self.get_new_tickets(self.portal_user)
        self.assertIn(self.portal_ticket, tickets)
        self.assertIn(self.new_ticket_title, tickets.mapped("name"))
