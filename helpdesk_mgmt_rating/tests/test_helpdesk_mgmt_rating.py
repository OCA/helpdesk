# Copyright 2022 Tecnativa - Víctor Martínez
# Copyright 2024 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import new_test_user, users

from odoo.addons.base.tests.common import BaseCommon


class TestHelpdeskMgmtRating(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {"name": "Test partner", "email": "test@email.com"}
        )
        new_test_user(
            cls.env,
            login="test-helpdesk-user",
            groups="helpdesk_mgmt.group_helpdesk_user",
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
                "user_id": self.env.user.id,
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
        # Check action view ticket rating
        action = ticket.action_view_ticket_rating()
        self.assertEqual(action.get("type"), "ir.actions.act_window")
        self.assertEqual(action.get("name"), "Ticket Rating")
        self.assertEqual(
            action.get("id"),
            self.env.ref("helpdesk_mgmt_rating.helpdesk_ticket_rating_action").id,
        )
