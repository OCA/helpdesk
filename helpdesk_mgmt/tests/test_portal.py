from odoo import http
from odoo.tests.common import new_test_user

from odoo.addons.base.tests.common import HttpCaseWithUserPortal


class TestPortal(HttpCaseWithUserPortal):
    """Test controllers defined for portal mode.
    This is mostly for basic coverage; we don't go as far as fully validating
    HTML produced by our routes.
    """

    def setUp(self):
        super().setUp()
        # Create a basic user with no helpdesk permissions.
        new_test_user(self.env, login="test-basic-user")
        # Create a ticket submitted by our portal user.
        self.portal_ticket = self._create_ticket(
            self.partner_portal, "portal-ticket-title"
        )

    def test_ticket_list(self):
        """List tickets in portal mode, ensure it contains our test ticket."""
        self.authenticate("portal", "portal")
        resp = self.url_open("/my/tickets")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("portal-ticket-title", resp.text)

    def test_ticket_form(self):
        """Open our test ticket in portal mode."""
        self.authenticate("portal", "portal")
        resp = self.url_open(f"/my/ticket/{self.portal_ticket.id}")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("portal-ticket-title", resp.text)
        self.assertIn(
            "<h4><strong>Message and communication history</strong></h4>", resp.text
        )

    def test_submit_ticket(self):
        """Submit a ticket in portal mode."""
        new_ticket_title = "portal-new-submitted-ticket-subject"
        new_ticket_desc_lines = (  # multiline description to check line breaks
            "portal-new-submitted-ticket-description-line-1",
            "portal-new-submitted-ticket-description-line-2",
        )

        def get_new_tickets():
            return self.env["helpdesk.ticket"].search([("name", "=", new_ticket_title)])

        self.assertEqual(len(get_new_tickets()), 0)  # not found so far

        self.authenticate("portal", "portal")
        resp = self.url_open(
            "/submitted/ticket",
            data={
                "category": self.env.ref("helpdesk_mgmt.helpdesk_category_1").id,
                "csrf_token": http.WebRequest.csrf_token(self),
                "subject": new_ticket_title,
                "description": "\n".join(new_ticket_desc_lines),
            },
        )
        self.assertEqual(resp.status_code, 200)
        ticket = get_new_tickets()
        self.assertEqual(len(ticket), 1)  # new ticket found
        self.assertEqual(
            ticket.description, "<p>" + "<br>".join(new_ticket_desc_lines) + "</p>"
        )

    def test_ticket_list_unauthenticated(self):
        """Attempt to list tickets without auth, ensure we get sent back to login."""
        resp = self.url_open("/my/tickets", allow_redirects=False)
        self.assertEqual(resp.status_code, 303)
        self.assertTrue(resp.is_redirect)
        # http://127.0.0.1:8069/web/login?redirect=http%3A%2F%2F127.0.0.1%3A8069%2Fmy%2Ftickets
        self.assertIn("/web/login", resp.headers["Location"])

    def test_ticket_list_unauthorized(self):
        """Attempt to list tickets without helpdesk permissions, ensure we get
        sent back to /my.
        """
        self.authenticate("test-basic-user", "test-basic-user")
        resp = self.url_open("/my/tickets", allow_redirects=False)
        self.assertEqual(resp.status_code, 303)
        self.assertTrue(resp.is_redirect)
        # http://127.0.0.1:8069/my
        self.assertTrue(resp.headers["Location"].endswith("/my"))

    def test_tickets_2_users(self):
        """Check tickets between 2 portal users; ensure they can't access each
        others' tickets.
        """
        portal_user_1 = self.user_portal  # created by HttpCaseWithUserPortal
        portal_user_2 = self.user_portal.copy(
            default={"login": "portal2", "password": "portal2"}
        )

        ticket_1 = self._create_ticket(portal_user_1.partner_id, "ticket-user-1")
        ticket_2 = self._create_ticket(portal_user_2.partner_id, "ticket-user-2")

        # Portal ticket list: portal_user_1 only sees ticket_1
        self.authenticate("portal", "portal")
        resp = self.url_open("/my/tickets")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("ticket-user-1", resp.text)
        self.assertNotIn("ticket-user-2", resp.text)

        # Portal ticket list: portal_user_2 only sees ticket_2
        self.authenticate("portal2", "portal2")
        resp = self.url_open("/my/tickets")
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn("ticket-user-1", resp.text)
        self.assertIn("ticket-user-2", resp.text)

        # Portal ticket form: portal_user_1 can open ticket_1 but not ticket_2
        self.authenticate("portal", "portal")
        resp = self.url_open(f"/my/ticket/{ticket_1.id}")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("ticket-user-1", resp.text)
        resp = self.url_open(f"/my/ticket/{ticket_2.id}", allow_redirects=False)
        self.assertEqual(resp.status_code, 303)
        self.assertTrue(resp.is_redirect)
        self.assertTrue(resp.headers["Location"].endswith("/my"))

        # Portal ticket form: portal_user_2 can open ticket_2 but not ticket_1
        self.authenticate("portal2", "portal2")
        resp = self.url_open(f"/my/ticket/{ticket_1.id}", allow_redirects=False)
        self.assertEqual(resp.status_code, 303)
        self.assertTrue(resp.is_redirect)
        self.assertTrue(resp.headers["Location"].endswith("/my"))
        resp = self.url_open(f"/my/ticket/{ticket_2.id}")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("ticket-user-2", resp.text)

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
