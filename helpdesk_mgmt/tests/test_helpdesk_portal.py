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
        self.basic_user = new_test_user(
            self.env, login="test-user", password="test-user", context=ctx
        )
        self.portal_user = new_test_user(
            self.env,
            login="test-portal",
            password="test-portal",
            groups="base.group_portal",
            context=ctx,
        )
        self.new_ticket_title = "portal-new-submitted-ticket-subject"
        self.new_ticket_desc_lines = (  # multiline description to check line breaks
            "portal-new-submitted-ticket-description-line-1",
            "portal-new-submitted-ticket-description-line-2",
        )

    def get_new_tickets(self, user, name):
        return self.env["helpdesk.ticket"].with_user(user).search([("name", "=", name)])

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
        tickets = self.get_new_tickets(self.basic_user, self.new_ticket_title)
        self.assertEqual(len(tickets), 1)

    def test_submit_ticket_02(self):
        self.authenticate("test-portal", "test-portal")
        self._submit_ticket()
        tickets = self.get_new_tickets(self.portal_user, self.new_ticket_title)
        self.assertEqual(len(tickets), 1)
