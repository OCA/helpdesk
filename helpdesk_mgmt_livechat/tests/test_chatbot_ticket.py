# Copyright 2025 Marcel Savegnago - Escodoo <https://escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import users

from odoo.addons.helpdesk_mgmt_livechat.tests import chatbot_common


class TestChatbotTicket(chatbot_common.HelpdeskChatbotCase):
    @users("user_public")
    def test_chatbot_ticket_public_user(self):
        self._chatbot_create_ticket(self.user_public)

        created_ticket = (
            self.env["helpdesk.ticket"].sudo().search([], limit=1, order="id desc")
        )
        self.assertEqual(created_ticket.name, "Testing Bot's New Ticket")
        self.assertEqual(created_ticket.partner_email, "test2@example.com")
        self.assertEqual(created_ticket.partner_name, "")
        self.assertEqual(created_ticket.team_id, self.helpdesk_team)
        self.assertIn("Livechat", created_ticket.channel_id.name)

    @users("user_portal")
    def test_chatbot_ticket_portal_user(self):
        self.step_create_ticket.write({"helpdesk_team_id": self.helpdesk_team})
        self._chatbot_create_ticket(self.user_portal)

        created_ticket = (
            self.env["helpdesk.ticket"].sudo().search([], limit=1, order="id desc")
        )
        self.assertEqual(created_ticket.name, "Testing Bot's New Ticket")
        self.assertEqual(created_ticket.partner_id, self.user_portal.partner_id)
        self.assertEqual(created_ticket.team_id, self.helpdesk_team)
        self.assertIn("Livechat", created_ticket.channel_id.name)

    def _chatbot_create_ticket(self, user):
        channel_info = self.livechat_channel._open_livechat_mail_channel(
            anonymous_name="Test Visitor",
            chatbot_script=self.chatbot_script,
            user_id=user.id,
        )
        mail_channel = self.env["mail.channel"].sudo().browse(channel_info["id"])

        self._post_answer_and_trigger_next_step(
            mail_channel,
            self.step_dispatch_create_ticket.name,
            chatbot_script_answer=self.step_dispatch_create_ticket,
        )
        self.assertEqual(
            mail_channel.chatbot_current_step_id, self.step_create_ticket_email
        )
        self._post_answer_and_trigger_next_step(mail_channel, "test2@example.com")

        self.assertEqual(
            mail_channel.chatbot_current_step_id, self.step_create_ticket_phone
        )
        self._post_answer_and_trigger_next_step(mail_channel, "123456")

        self.assertEqual(mail_channel.chatbot_current_step_id, self.step_create_ticket)
