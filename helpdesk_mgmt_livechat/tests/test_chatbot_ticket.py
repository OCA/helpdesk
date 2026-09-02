# Copyright 2025 Marcel Savegnago - Escodoo <https://escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from unittest.mock import patch

import odoo.api
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

    @users("user_public")
    def test_chatbot_ticket_fallback_channel_found_by_search(self):
        livechat_channel = (
            self.env["helpdesk.ticket.channel"]
            .sudo()
            .search([("name", "=", "Livechat")], limit=1)
        )
        if not livechat_channel:
            livechat_channel = (
                self.env["helpdesk.ticket.channel"].sudo().create({"name": "Livechat"})
            )

        mail_channel = self._setup_chatbot_mail_channel(self.user_public)

        original_ref = odoo.api.Environment.ref

        def mock_ref(env_self, xmlid, raise_if_not_found=True):
            if xmlid == "helpdesk_mgmt_livechat.helpdesk_ticket_channel_livechat":
                return env_self["helpdesk.ticket.channel"].browse()
            return original_ref(env_self, xmlid, raise_if_not_found=raise_if_not_found)

        with patch.object(odoo.api.Environment, "ref", mock_ref):
            self._post_answer_and_trigger_next_step(mail_channel, "123456")

        self.assertEqual(mail_channel.chatbot_current_step_id, self.step_create_ticket)
        created_ticket = (
            self.env["helpdesk.ticket"].sudo().search([], limit=1, order="id desc")
        )
        self.assertEqual(created_ticket.name, "Testing Bot's New Ticket")
        self.assertEqual(created_ticket.channel_id, livechat_channel)

    @users("user_public")
    def test_chatbot_ticket_fallback_channel_created(self):
        mail_channel = self._setup_chatbot_mail_channel(self.user_public)
        TicketChannel = self.env["helpdesk.ticket.channel"]

        original_ref = odoo.api.Environment.ref

        def mock_ref(env_self, xmlid, raise_if_not_found=True):
            if xmlid == "helpdesk_mgmt_livechat.helpdesk_ticket_channel_livechat":
                return env_self["helpdesk.ticket.channel"].browse()
            return original_ref(env_self, xmlid, raise_if_not_found=raise_if_not_found)

        _original_search = type(TicketChannel).search

        def mock_search(model_self, domain, *args, **kwargs):
            if domain == [("name", "=", "Livechat")]:
                return TicketChannel.browse()
            return _original_search(model_self, domain, *args, **kwargs)

        with (
            patch.object(odoo.api.Environment, "ref", mock_ref),
            patch.object(type(TicketChannel), "search", mock_search),
        ):
            self._post_answer_and_trigger_next_step(mail_channel, "123456")

        self.assertEqual(mail_channel.chatbot_current_step_id, self.step_create_ticket)
        created_ticket = (
            self.env["helpdesk.ticket"].sudo().search([], limit=1, order="id desc")
        )
        self.assertEqual(created_ticket.name, "Testing Bot's New Ticket")
        self.assertEqual(created_ticket.channel_id.name, "Livechat")

    def _setup_chatbot_mail_channel(self, user):
        """Set up a chatbot discuss channel through the email and phone steps."""
        discuss_channel_vals = self.livechat_channel._get_livechat_discuss_channel_vals(
            anonymous_name="Test Visitor",
            chatbot_script=self.chatbot_script,
            user_id=user.id,
            country_id=self.company_id.country_id.id,
            lang=False,
        )
        mail_channel = self.env["discuss.channel"].sudo().create(discuss_channel_vals)
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
        return mail_channel

    def _chatbot_create_ticket(self, user):
        mail_channel = self._setup_chatbot_mail_channel(user)
        self._post_answer_and_trigger_next_step(mail_channel, "123456")
        self.assertEqual(mail_channel.chatbot_current_step_id, self.step_create_ticket)
