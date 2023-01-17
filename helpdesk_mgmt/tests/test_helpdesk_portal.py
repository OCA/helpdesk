# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import odoo.tests
from odoo import http
from odoo.tests import new_test_user


class TestHelpdeskPortalBase(odoo.tests.HttpCase):
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

    def _create_ticket(self, partner, ticket_title, **values):
        """Create a ticket submitted by the specified partner."""
        data = {
            "name": ticket_title,
            "description": "test-description",
            "partner_id": partner.id,
            "partner_email": partner.email,
            "partner_name": partner.name,
        }
        data.update(**values)
        return self.env["helpdesk.ticket"].create(data)

    def _submit_ticket(self, **values):
        data = {
            "category": self.env.ref("helpdesk_mgmt.helpdesk_category_1").id,
            "csrf_token": http.WebRequest.csrf_token(self),
            "subject": self.new_ticket_title,
            "description": "\n".join(self.new_ticket_desc_lines),
        }
        data.update(**values)
        resp = self.url_open("/submitted/ticket", data=data)
        self.assertEqual(resp.status_code, 200)

    def _count_close_buttons(self, resp) -> int:
        """Count close buttons in a form by counting forms with that target."""
        return resp.text.count('action="/ticket/close"')

    def _call_close_ticket(self, ticket, stage):
        """Call /ticket/close with the specified target stage, check redirect."""
        resp = self.url_open(
            "/ticket/close",
            data={
                "csrf_token": http.WebRequest.csrf_token(self),
                "stage_id": stage.id,
                "ticket_id": ticket.id,
            },
            allow_redirects=False,
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.is_redirect)  # http://127.0.0.1:8069/my/ticket/<ticket-id>
        self.assertTrue(resp.headers["Location"].endswith(f"/my/ticket/{ticket.id}"))
        return resp


@odoo.tests.tagged("post_install", "-at_install")
class TestHelpdeskPortal(TestHelpdeskPortalBase):
    def test_submit_ticket_01(self):
        self.authenticate("test-user", "test-user")
        self._submit_ticket()
        tickets = self.get_new_tickets(self.basic_user)
        self.assertNotIn(self.portal_ticket, tickets)
        self.assertIn(self.new_ticket_title, tickets.mapped("name"))
        self.assertIn(
            "<p>" + "<br>".join(self.new_ticket_desc_lines) + "</p>",
            tickets.mapped("description"),
        )

    def test_submit_ticket_02(self):
        self.authenticate("test-portal", "test-portal")
        self._submit_ticket()
        tickets = self.get_new_tickets(self.portal_user)
        self.assertIn(self.portal_ticket, tickets)
        self.assertIn(self.new_ticket_title, tickets.mapped("name"))
        self.assertIn(
            "<p>" + "<br>".join(self.new_ticket_desc_lines) + "</p>",
            tickets.mapped("description"),
        )

    def test_close_ticket(self):
        """Close a ticket from the portal."""
        self.assertFalse(self.portal_ticket.closed)
        self.authenticate("test-portal", "test-portal")
        resp = self.url_open(f"/my/ticket/{self.portal_ticket.id}")
        self.assertEqual(self._count_close_buttons(resp), 2)  # 2 close stages in data/
        stage = self.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_done")
        self._call_close_ticket(self.portal_ticket, stage)
        self.assertTrue(self.portal_ticket.closed)
        self.assertEqual(self.portal_ticket.stage_id, stage)
        resp = self.url_open(f"/my/ticket/{self.portal_ticket.id}")
        self.assertEqual(self._count_close_buttons(resp), 0)  # no close buttons now

    def test_close_ticket_invalid_stage(self):
        """Attempt to close a ticket from the portal with an invalid target stage."""
        self.authenticate("test-portal", "test-portal")
        stage = self.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_awaiting")
        self._call_close_ticket(self.portal_ticket, stage)
        self.assertFalse(self.portal_ticket.closed)
        self.assertNotEqual(self.portal_ticket.stage_id, stage)
