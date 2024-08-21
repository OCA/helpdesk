# Copyright 2024 Akretion (https://www.akretion.com).
# @author Olivier Nibart <olivier.nibart@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest import mock

from odoo.tests.common import SavepointCase


class TestTicketReopen(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.MailMessage = cls.env["mail.message"]

        cls.stage_new = cls.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_new")
        cls.stage_in_progress = cls.env.ref(
            "helpdesk_mgmt.helpdesk_ticket_stage_in_progress"
        )
        cls.stage_closed = cls.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_done")

        cls.ticket = cls.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "Description",
            }
        )

    def test_is_reopener_message(self):
        vals = {
            "model": "not helpdesk.ticket",
            "message_type": "not comment or notification",
        }
        self.assertFalse(self.MailMessage.is_reopener_message(vals))
        vals = {
            "model": "helpdesk.ticket",
            "message_type": "notification",
        }
        self.assertFalse(self.MailMessage.is_reopener_message(vals))
        vals = {
            "model": "helpdesk.ticket",
            "message_type": "comment",
        }
        # type comment in production is not a reopener
        self.assertTrue(self.MailMessage.is_production_env())
        self.assertFalse(self.MailMessage.is_reopener_message(vals))
        # type comment not in production is a reopener
        with mock.patch.object(
            type(self.MailMessage),
            "is_production_env",
            return_value=False,
        ):
            self.assertFalse(self.MailMessage.is_production_env())
            self.assertTrue(self.MailMessage.is_reopener_message(vals))
        vals = {
            "model": "helpdesk.ticket",
            "message_type": "not comment or notification",
        }
        self.assertTrue(self.MailMessage.is_reopener_message(vals))

    def test_helpdesk_ticket_new_reopen(self):
        self.assertEqual(self.ticket.stage_id, self.stage_new)
        self.ticket.message_post(
            body="Test message of type email",
            message_type="email",
        )
        self.assertEqual(self.ticket.stage_id, self.stage_new)

    def test_helpdesk_ticket_in_progress_reopen(self):
        self.ticket.stage_id = self.stage_in_progress
        self.ticket.message_post(
            body="Test message of type email",
            message_type="email",
        )
        self.assertEqual(self.ticket.stage_id, self.stage_in_progress)

    def test_helpdesk_ticket_closed_reopen(self):
        self.ticket.stage_id = self.stage_closed
        self.ticket.message_post(
            body="Test message of type email",
            message_type="email",
        )
        self.assertEqual(self.ticket.stage_id, self.stage_new)
