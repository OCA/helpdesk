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
            model="helpdesk.ticket",
            message=message,
            save_original=False,
            strip_attachments=True,
        )
        ticket_number = self.env["helpdesk.ticket"].browse(res_id).number
        self.assertEqual(ticket_number[:2], "HT")
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

    def _create_autoreply_template(self):
        """Return a minimal mail.template for helpdesk.ticket."""
        return self.env["mail.template"].create(
            {
                "name": "Test Auto Reply",
                "model_id": self.env.ref("helpdesk_mgmt.model_helpdesk_ticket").id,
                "subject": "We received your ticket",
                "body_html": "<p>Thank you for contacting us!</p>",
            }
        )

    def _create_ignored_partner(self, email, name=None):
        """Create a res.partner with the given email and add it to the company's
        autoreply ignore list."""
        partner = self.env["res.partner"].create(
            {"name": name or email, "email": email}
        )
        self.company.helpdesk_mgmt_autoreply_ignored_partners = [(4, partner.id)]
        return partner

    def test_autoreply_sent_for_normal_email(self):
        """_track_template includes the stage template for a non-ignored sender."""
        mail_template = self._create_autoreply_template()
        self.new_stage.mail_template_id = mail_template
        # configure an ignored partner whose email differs from the ticket sender
        self._create_ignored_partner("noreply@monitoring.example.com")
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Normal customer ticket",
                "description": "I need help",
                "team_id": self.team_a.id,
                "stage_id": self.new_stage.id,
                "partner_email": "customer@example.com",
            }
        )
        result = ticket._track_template({"stage_id": self.new_stage})
        self.assertIn(
            "stage_id",
            result,
            "Auto-reply template should be present for a non-ignored sender.",
        )

    def test_autoreply_not_sent_for_ignored_partner(self):
        """Stage template is skipped when the ticket sender is an ignored partner."""
        mail_template = self._create_autoreply_template()
        self.new_stage.mail_template_id = mail_template
        ignored_email = "noreply@monitoring.example.com"
        self._create_ignored_partner(ignored_email)
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Alert from monitoring system",
                "description": "Automated alert",
                "team_id": self.team_a.id,
                "stage_id": self.new_stage.id,
                "partner_email": ignored_email,
            }
        )
        result = ticket._track_template({"stage_id": self.new_stage})
        self.assertNotIn(
            "stage_id",
            result,
            "Auto-reply template should be absent for an ignored sender.",
        )

    def test_autoreply_ignored_partner_email_is_normalized(self):
        """Ignore list matching is case-insensitive (via email_normalize)."""
        mail_template = self._create_autoreply_template()
        self.new_stage.mail_template_id = mail_template
        # store the partner's address in upper case
        self._create_ignored_partner("NOREPLY@MONITORING.EXAMPLE.COM")
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Alert from monitoring system",
                "description": "Automated alert",
                "team_id": self.team_a.id,
                "stage_id": self.new_stage.id,
                # ticket arrives with the address in a display-name format
                "partner_email": "Monitoring Bot <noreply@monitoring.example.com>",
            }
        )
        result = ticket._track_template({"stage_id": self.new_stage})
        self.assertNotIn(
            "stage_id",
            result,
            "Ignore list matching should normalize both sides via email_normalize.",
        )

    def test_autoreply_multiple_ignored_partners(self):
        """Multiple ignored partners all suppress the auto-reply."""
        mail_template = self._create_autoreply_template()
        self.new_stage.mail_template_id = mail_template
        emails = [
            "alerts@example.com",
            "noreply@example.com",
            "monitoring@example.com",
        ]
        for email in emails:
            self._create_ignored_partner(email)
        for email in emails:
            ticket = self.env["helpdesk.ticket"].create(
                {
                    "name": f"Alert from {email}",
                    "description": "Automated alert",
                    "team_id": self.team_a.id,
                    "stage_id": self.new_stage.id,
                    "partner_email": email,
                }
            )
            result = ticket._track_template({"stage_id": self.new_stage})
            self.assertNotIn(
                "stage_id",
                result,
                f"Auto-reply should be suppressed for ignored address {email}.",
            )
