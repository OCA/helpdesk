# Copyright 2025 Marcel Savegnago - Escodoo <https://escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from unittest.mock import patch

from odoo.tests.common import users

from odoo.addons.helpdesk_mgmt.tests.common import TestHelpdeskTicketBase
from odoo.addons.mail.tests.common import mail_new_test_user


class TestLivechatTicket(TestHelpdeskTicketBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

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
        channel = self.env["discuss.channel"].create(
            {
                "name": "Chat with Visitor",
                "channel_member_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": self.env.user.partner_id.id,
                        },
                    )
                ],
            }
        )
        ticket = channel._convert_visitor_to_ticket(
            self.env.user.partner_id, "/ticket TestTicket command"
        )

        self.assertEqual(
            channel.channel_partner_ids,
            self.user.partner_id,
        )
        self.assertEqual(ticket.name, "TestTicket command")
        self.assertFalse(ticket.partner_id)
        self.assertEqual(ticket.channel_id, self.livechat_channel)

        # another internal operator invited: still no partner on ticket
        channel.write(
            {
                "channel_member_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": self.user_team.partner_id.id,
                        },
                    )
                ]
            }
        )
        ticket = channel._convert_visitor_to_ticket(
            self.env.user.partner_id, "/ticket TestTicket command"
        )
        self.assertFalse(ticket.partner_id)
        self.assertEqual(ticket.channel_id, self.livechat_channel)

    @users("helpdesk_mgmt-user")
    def test_helpdesk_ticket_creation_portal(self):
        """Test ticket creation from livechat with portal user"""
        # portal: should be set as partner
        channel = self.env["discuss.channel"].create(
            {
                "name": "Chat with Visitor",
                "channel_member_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": self.env.user.partner_id.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "partner_id": self.user_portal.partner_id.id,
                        },
                    ),
                ],
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

    @users("helpdesk_mgmt-user")
    def test_helpdesk_ticket_creation_public_user_resets_customers(self):
        """Quando existir um parceiro público no canal, o ticket não deve
        ficar vinculado a nenhum partner específico (modo anônimo)."""
        channel = self.env["discuss.channel"].create(
            {
                "name": "Chat with Visitor",
                "channel_member_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": self.env.user.partner_id.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "partner_id": self.user_portal.partner_id.id,
                        },
                    ),
                ],
            }
        )

        # Simula que, ao iterar sobre os partners do canal, há um partner público.
        public_partner = self.user_anonymous.partner_id

        with patch.object(
            type(channel.channel_partner_ids),
            "filtered",
            return_value=public_partner,
        ):
            ticket = channel._convert_visitor_to_ticket(
                self.env.user.partner_id, "/ticket Public user present"
            )

        # Como existe parceiro público (simulado), o ticket deve ficar sem partner
        self.assertFalse(ticket.partner_id)

    @users("helpdesk_mgmt-user")
    def test_helpdesk_ticket_command_without_title(self):
        """Test /ticket command without title"""
        channel = self.env["discuss.channel"].create(
            {
                "name": "Chat with Visitor",
                "channel_member_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": self.env.user.partner_id.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "partner_id": self.user_portal.partner_id.id,
                        },
                    ),
                ],
            }
        )
        # Test command without title
        channel.execute_command_ticket(body="/ticket")
        # Should not create a ticket, just show help message

    @users("helpdesk_mgmt-user")
    def test_convert_visitor_to_ticket_creates_livechat_channel_if_missing(self):
        """Se o canal Livechat não existir (nem por XML ID, nem por nome),
        o método deve criá-lo antes de criar o ticket."""
        channel = self.env["discuss.channel"].create(
            {
                "name": "Chat with Visitor",
                "channel_member_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": self.env.user.partner_id.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "partner_id": self.user_portal.partner_id.id,
                        },
                    ),
                ],
            }
        )

        TicketChannel = self.env["helpdesk.ticket.channel"]

        # Garantir que nem o XML ID nem a busca por nome encontrem um canal existente,
        # forçando o caminho que cria o canal \"Livechat\".
        with (
            patch.object(self.env, "ref", return_value=TicketChannel.browse()),
            patch.object(
                type(TicketChannel), "search", return_value=TicketChannel.browse()
            ),
        ):
            ticket = channel._convert_visitor_to_ticket(
                self.env.user.partner_id, "/ticket Issue without channel"
            )

        self.assertTrue(ticket.channel_id)
        self.assertEqual(ticket.channel_id.name, "Livechat")

    @users("helpdesk_mgmt-user")
    def test_execute_command_ticket_with_title(self):
        """Test /ticket command with title creates ticket
        and sends transient message."""
        channel = self.env["discuss.channel"].create(
            {
                "name": "Chat with Visitor",
                "channel_member_ids": [
                    (0, 0, {"partner_id": self.env.user.partner_id.id}),
                    (0, 0, {"partner_id": self.user_portal.partner_id.id}),
                ],
            }
        )
        count_before = self.env["helpdesk.ticket"].search_count([])
        channel.execute_command_ticket(body="/ticket Issue with login")
        count_after = self.env["helpdesk.ticket"].search_count([])
        self.assertEqual(count_after, count_before + 1)
        ticket = self.env["helpdesk.ticket"].search([], limit=1, order="id desc")
        self.assertEqual(ticket.name, "Issue with login")
        self.assertEqual(ticket.partner_id, self.user_portal.partner_id)
        self.assertEqual(ticket.channel_id, self.livechat_channel)

    @users("helpdesk_mgmt-user")
    def test_convert_visitor_to_ticket_description_contains_history(self):
        """Test that created ticket description contains channel message history."""
        channel = self.env["discuss.channel"].create(
            {
                "name": "Chat with Visitor",
                "channel_member_ids": [
                    (0, 0, {"partner_id": self.env.user.partner_id.id}),
                    (0, 0, {"partner_id": self.user_portal.partner_id.id}),
                ],
            }
        )
        channel.message_post(body="Hello, I need help with my order.")
        ticket = channel._convert_visitor_to_ticket(
            self.env.user.partner_id, "/ticket Order help"
        )
        self.assertIn("Order help", ticket.name)
        self.assertTrue(ticket.description)
        self.assertIn("Hello", ticket.description)
