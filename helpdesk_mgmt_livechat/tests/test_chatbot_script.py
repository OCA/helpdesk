# Copyright 2025 Marcel Savegnago - Escodoo <https://escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import users

from odoo.addons.helpdesk_mgmt.tests.common import TestHelpdeskTicketBase


class TestChatbotScriptTicketCount(TestHelpdeskTicketBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.chatbot_script = (
            cls.env["chatbot.script"].sudo().create({"title": "Support Bot"})
        )
        cls.livechat_channel = (
            cls.env["helpdesk.ticket.channel"]
            .sudo()
            .search([("name", "=", "Livechat")], limit=1)
        )
        if not cls.livechat_channel:
            cls.livechat_channel = (
                cls.env["helpdesk.ticket.channel"].sudo().create({"name": "Livechat"})
            )

    @users("helpdesk_mgmt-user")
    def test_ticket_count_zero(self):
        """ticket_count is 0 when no tickets match script title and Livechat channel."""
        self.assertEqual(self.chatbot_script.ticket_count, 0)

    @users("helpdesk_mgmt-user")
    def test_ticket_count_computed(self):
        """ticket_count counts tickets with description ilike
        script title and channel Livechat."""
        self.env["helpdesk.ticket"].create(
            {
                "name": "Ticket 1",
                "description": "Chat with Support Bot: user asked for help",
                "channel_id": self.livechat_channel.id,
            }
        )
        self.env["helpdesk.ticket"].create(
            {
                "name": "Ticket 2",
                "description": "Support Bot conversation",
                "channel_id": self.livechat_channel.id,
            }
        )
        self.chatbot_script.invalidate_recordset(["ticket_count"])
        self.assertEqual(self.chatbot_script.ticket_count, 2)

        # Ticket with different channel not counted
        other_channel = (
            self.env["helpdesk.ticket.channel"].sudo().create({"name": "Email"})
        )
        self.env["helpdesk.ticket"].create(
            {
                "name": "Ticket 3",
                "description": "Support Bot via email",
                "channel_id": other_channel.id,
            }
        )
        self.chatbot_script.invalidate_recordset(["ticket_count"])
        self.assertEqual(self.chatbot_script.ticket_count, 2)

    @users("helpdesk_mgmt-user")
    def test_ticket_count_other_script_not_counted(self):
        """Tickets with description not containing script title are not counted."""
        other_script = self.env["chatbot.script"].sudo().create({"title": "Sales Bot"})
        self.env["helpdesk.ticket"].create(
            {
                "name": "Ticket",
                "description": "Sales Bot conversation",
                "channel_id": self.livechat_channel.id,
            }
        )
        self.chatbot_script.invalidate_recordset(["ticket_count"])
        other_script.invalidate_recordset(["ticket_count"])
        self.assertEqual(self.chatbot_script.ticket_count, 0)
        self.assertEqual(other_script.ticket_count, 1)

    @users("helpdesk_mgmt-user")
    def test_action_view_tickets(self):
        """action_view_tickets returns action with domain and context."""
        action = self.chatbot_script.action_view_tickets()
        self.assertEqual(action["res_model"], "helpdesk.ticket")
        self.assertEqual(
            action["domain"],
            [
                ("description", "ilike", self.chatbot_script.title),
                ("channel_id.name", "=", "Livechat"),
            ],
        )
        self.assertEqual(action["context"], {"create": False})
