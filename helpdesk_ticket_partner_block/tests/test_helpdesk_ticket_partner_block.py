# Copyright 2026 Paloma González-Ripoll(APSL-Nagarro)<paloma.gonzalez@nagarro.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.mail.tests.common import MailCommon

RAW_EMAIL = """From: {name} <{email}>
To: helpdesk@example.com
Subject: {subject}
Message-Id: <{msgid}@example.com>
Content-Type: text/plain; charset="utf-8"

This is the body of the test email.
"""


class TestHelpdeskTicketPartnerBlock(MailCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.blocked_partner = cls.env["res.partner"].create(
            {
                "name": "Blocked Partner",
                "email": "blocked@example.com",
                "block_ticket_creation": True,
            }
        )
        cls.normal_partner = cls.env["res.partner"].create(
            {
                "name": "Normal Partner",
                "email": "normal@example.com",
                "block_ticket_creation": False,
            }
        )

    def _process_email(self, partner, msgid):
        raw = RAW_EMAIL.format(
            name=partner.name,
            email=partner.email,
            subject="Test email",
            msgid=msgid,
        )
        return self.env["mail.thread"].message_process("helpdesk.ticket", raw.encode())

    def test_blocked_partner_does_not_create_ticket(self):
        with self.mock_mail_gateway():
            thread_id = self._process_email(self.blocked_partner, "blocked-test")
        self.assertFalse(thread_id)
        ticket = self.env["helpdesk.ticket"].search(
            [("partner_id", "=", self.blocked_partner.id)]
        )
        self.assertFalse(ticket)
        self.assertTrue(
            any(mail.email_to == self.blocked_partner.email for mail in self._new_mails)
        )

    def test_normal_partner_creates_ticket(self):
        with self.mock_mail_gateway():
            thread_id = self._process_email(self.normal_partner, "normal-test")
        self.assertTrue(thread_id)
        ticket = self.env["helpdesk.ticket"].browse(thread_id)
        self.assertEqual(ticket.partner_id, self.normal_partner)
        self.assertFalse(self._new_mails)
