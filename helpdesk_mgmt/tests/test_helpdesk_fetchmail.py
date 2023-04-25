# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from .common import TestHelpdeskTicketBase

EMAIL_TPL = """Return-Path: <whatever-2a840@postmaster.twitter.com>
X-Original-To: {to}
Delivered-To: {to}
To: {to}
Received: by mail1.odoo.com (Postfix, from userid 10002)
    id 5DF9ABFB2A; Fri, 10 Aug 2012 16:16:39 +0200 (CEST)
Message-ID: {msg_id}
Date: Tue, 29 Nov 2011 12:43:21 +0530
From: {email_from}
MIME-Version: 1.0
Subject: {subject}
Content-Type: text/plain; charset=ISO-8859-1; format=flowed

Hello,

This email should create a new entry in your module. Please check that it
effectively works.

Thanks,

--
Raoul Boitempoils
Integrator at Agrolait"""


class TestHelpdeskFetchmail(TestHelpdeskTicketBase):
    """ """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.channel_email = cls.env.ref("helpdesk_mgmt.helpdesk_ticket_channel_email")

    def _dummy_fetchmail_process(self):
        """In a real case workflow, the `fetchmail.server::fetch_mail()` function
        fetches IMAP/POP servers and creates new messages objects using
        `mail.thread::message_process()`."""
        MailThread = self.env["mail.thread"]
        additional_context = {"fetchmail_cron_running": True}
        message = EMAIL_TPL.format(
            to="general-alias-for-tickets@local.test",
            subject="Need backup",
            email_from="bob@mycompany.com",
            msg_id="168242744424.20.2028152230359369389@dd607af32153",
        )
        res_id = MailThread.with_context(**additional_context).message_process(
            model=False,
            message=message,
            save_original=False,
            strip_attachments=True,
        )
        self.assertGreater(res_id, 0)

    def test_message_process(self):
        # keep a list of existing tickets
        ticket_ids = self.env["helpdesk.ticket"].search([])
        self._dummy_fetchmail_process()
        # get the newly created ticket
        ticket_id = self.env["helpdesk.ticket"].search([]) - ticket_ids
        self.assertEqual(len(ticket_id), 1)
        self.assertEqual(ticket_id.name, "Need backup")
        # ensure that the e-mail channel has been set automatically
        self.assertEqual(ticket_id.channel_id, self.channel_email)

    def test_message_process_missing_channel(self):
        # delete default e-mail channel
        self.channel_email.unlink()
        # keep a list of existing tickets
        ticket_ids = self.env["helpdesk.ticket"].search([])
        self._dummy_fetchmail_process()
        # get the newly created ticket
        ticket_id = self.env["helpdesk.ticket"].search([]) - ticket_ids
        self.assertEqual(len(ticket_id), 1)
        self.assertEqual(ticket_id.name, "Need backup")
        # ensure that the channel is not set
        self.assertFalse(ticket_id.channel_id)
