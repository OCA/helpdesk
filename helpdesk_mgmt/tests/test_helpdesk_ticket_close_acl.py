# Copyright 2026 Grégory Mariani
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo.tests.common import tagged

from odoo.addons.base.tests.common import (
    DISABLED_MAIL_CONTEXT,
    HttpCaseWithUserPortal,
)


@tagged("post_install", "-at_install")
class TestHelpdeskTicketCloseACL(HttpCaseWithUserPortal):
    """Regression test for the /ticket/close access-control fix.

    The controller used to fetch the ticket with sudo() and only check the
    target stage's close_from_portal flag, letting a portal user change the
    stage of any ticket by passing an arbitrary ticket_id. The fix fetches the
    ticket as the current user so record rules apply.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.stage_open = cls.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_new")
        cls.stage_close = cls.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_done")
        # A partner unrelated to the portal user: its ticket is out of reach.
        cls.victim_partner = cls.env["res.partner"].create({"name": "Victim Corp ACL"})
        cls.victim_ticket = cls.env["helpdesk.ticket"].create(
            {
                "name": "victim-acl-ticket",
                "description": "victim",
                "partner_id": cls.victim_partner.id,
                "stage_id": cls.stage_open.id,
            }
        )
        # A ticket the portal user legitimately owns.
        cls.own_ticket = cls.env["helpdesk.ticket"].create(
            {
                "name": "own-acl-ticket",
                "description": "mine",
                "partner_id": cls.partner_portal.id,
                "stage_id": cls.stage_open.id,
            }
        )

    def _close(self, ticket, stage):
        return self.url_open(f"/ticket/close?ticket_id={ticket.id}&stage_id={stage.id}")

    def test_portal_cannot_close_foreign_ticket(self):
        # Precondition: the record rule already hides the ticket from the ORM.
        self.assertFalse(
            self.env["helpdesk.ticket"]
            .with_user(self.user_portal)
            .search([("id", "=", self.victim_ticket.id)]),
            "test setup invalid: portal user can read the victim ticket",
        )
        self.authenticate("portal", "portal")
        self._close(self.victim_ticket, self.stage_close)
        self.victim_ticket.invalidate_recordset()
        self.assertEqual(
            self.victim_ticket.stage_id,
            self.stage_open,
            "a portal user must not change the stage of a ticket it cannot access",
        )

    def test_portal_can_close_own_ticket(self):
        self.authenticate("portal", "portal")
        self._close(self.own_ticket, self.stage_close)
        self.own_ticket.invalidate_recordset()
        self.assertEqual(
            self.own_ticket.stage_id,
            self.stage_close,
            "a portal user must still be able to close its own ticket",
        )
