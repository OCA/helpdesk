# Copyright 2025 Marcel Savegnago - Escodoo <https://escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import users

from odoo.addons.helpdesk_mgmt.tests.common import TestHelpdeskTicketBase
from odoo.addons.mail.tests.common import mail_new_test_user


class TestLivechatTicket(TestHelpdeskTicketBase):
    @classmethod
    def setUpClass(cls):
        super(TestLivechatTicket, cls).setUpClass()

        cls.user_anonymous = mail_new_test_user(
            cls.env,
            login="user_anonymous",
            name="Anonymous Website",
            email=False,
            company_id=cls.env.company.id,
            notification_type="email",
            groups="base.group_public",
        )
        cls.user_portal = mail_new_test_user(
            cls.env,
            login="user_portal",
            name="Paulette Portal",
            email="user_portal@test.example.com",
            company_id=cls.env.company.id,
            notification_type="email",
            groups="base.group_portal",
        )

        # Get or create Livechat channel
        cls.livechat_channel = cls.env["helpdesk.ticket.channel"].search(
            [("name", "=", "Livechat")], limit=1
        )
        if not cls.livechat_channel:
            cls.livechat_channel = cls.env["helpdesk.ticket.channel"].create(
                {"name": "Livechat"}
            )

    @users("helpdesk_mgmt-user")
    def test_helpdesk_ticket_creation_guest(self):
        """Test ticket creation from livechat with guest user"""
        # public: should not be set as partner
        channel = self.env["mail.channel"].create(
            {
                "name": "Chat with Visitor",
                "channel_partner_ids": [(4, self.user_anonymous.partner_id.id)],
            }
        )
        ticket = channel._convert_visitor_to_ticket(
            self.env.user.partner_id, "/ticket TestTicket command"
        )

        self.assertEqual(
            channel.channel_partner_ids,
            self.user.partner_id | self.user_anonymous.partner_id,
        )
        self.assertEqual(ticket.name, "TestTicket command")
        self.assertFalse(ticket.partner_id)
        self.assertEqual(ticket.channel_id, self.livechat_channel)

        # public user: should not be set as partner
        channel = self.env["mail.channel"].create(
            {
                "name": "Chat with Visitor",
                "channel_partner_ids": [(4, self.env.ref("base.public_partner").id)],
            }
        )
        ticket = channel._convert_visitor_to_ticket(
            self.env.user.partner_id, "/ticket TestTicket command"
        )

        self.assertEqual(
            channel.channel_member_ids.partner_id,
            self.user.partner_id | self.env.ref("base.public_partner"),
        )
        self.assertEqual(ticket.name, "TestTicket command")
        self.assertFalse(ticket.partner_id)
        self.assertEqual(ticket.channel_id, self.livechat_channel)

        # public + someone else: no partner (as they were anonymous)
        channel.write({"channel_partner_ids": [(4, self.user_team.partner_id.id)]})
        ticket = channel._convert_visitor_to_ticket(
            self.env.user.partner_id, "/ticket TestTicket command"
        )
        self.assertFalse(ticket.partner_id)
        self.assertEqual(ticket.channel_id, self.livechat_channel)

    @users("helpdesk_mgmt-user")
    def test_helpdesk_ticket_creation_portal(self):
        """Test ticket creation from livechat with portal user"""
        # portal: should be set as partner
        channel = self.env["mail.channel"].create(
            {
                "name": "Chat with Visitor",
                "channel_partner_ids": [(4, self.user_portal.partner_id.id)],
            }
        )
        ticket = channel._convert_visitor_to_ticket(
            self.env.user.partner_id, "/ticket TestTicket command"
        )

        self.assertEqual(
            channel.channel_partner_ids,
            self.user.partner_id | self.user_portal.partner_id,
        )
        self.assertEqual(ticket.partner_id, self.user_portal.partner_id)
        self.assertEqual(ticket.channel_id, self.livechat_channel)

        # another operator invited: portal user should still be partner
        channel.write({"channel_partner_ids": [(4, self.user_team.partner_id.id)]})
        ticket = channel._convert_visitor_to_ticket(
            self.env.user.partner_id, "/ticket TestTicket command"
        )

        self.assertEqual(
            channel.channel_partner_ids,
            self.user.partner_id
            | self.user_portal.partner_id
            | self.user_team.partner_id,
        )
        self.assertEqual(ticket.partner_id, self.user_portal.partner_id)
        self.assertEqual(ticket.channel_id, self.livechat_channel)

    @users("helpdesk_mgmt-user")
    def test_helpdesk_ticket_command_without_title(self):
        """Test /ticket command without title"""
        channel = self.env["mail.channel"].create(
            {
                "name": "Chat with Visitor",
                "channel_partner_ids": [(4, self.user_portal.partner_id.id)],
            }
        )
        # Test command without title
        channel.execute_command_ticket(body="/ticket")
        # Should not create a ticket, just show help message
