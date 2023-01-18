# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common, new_test_user
from odoo.tests.common import users


class TestHelpdeskMgmtRating(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {"name": "Test partner", "email": "test@email.com"}
        )
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        new_test_user(
            cls.env,
            login="test-helpdesk-user",
            groups="helpdesk_mgmt.group_helpdesk_user",
            context=ctx,
        )
        cls.stage_done = cls.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_done")
        cls.stage_done.rating_mail_template_id = cls.env.ref(
            "helpdesk_mgmt_rating.rating_ticket_email_template"
        )

    @users("admin", "test-helpdesk-user")
    def test_ticket_stage_done(self):
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test 1",
                "description": "Ticket test",
                "partner_id": self.partner.id,
            }
        )
        old_messages = ticket.message_ids
        self.assertEqual(ticket.positive_rate_percentage, -1)
        ticket.write({"stage_id": self.stage_done.id})
        new_messages = ticket.message_ids - old_messages
        self.assertIn(self.partner, new_messages.mapped("partner_ids"))
        rating = ticket.rating_ids.filtered(lambda x: x.partner_id == self.partner)
        rating.write({"rating": 5, "consumed": True})
        self.assertEqual(ticket.positive_rate_percentage, 100)
