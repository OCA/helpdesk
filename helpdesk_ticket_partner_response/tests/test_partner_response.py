# Copyright 2024 Antoni Marroig(APSL-Nagarro)<amarroig@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.addons.base.tests.common import HttpCaseWithUserPortal

MAIL_TEMPLATE = """Return-Path: <whatever-2a840@postmaster.twitter.com>
To: {to}
Received: by mail1.openerp.com (Postfix, from userid 10002)
    id 5DF9ABFB2A; Fri, 30 May 2025 16:16:39 +0200 (CEST)
From: {email_from}
Subject: {subject}
MIME-Version: 1.0
Content-Type: multipart/alternative;
    boundary="----=_Part_4200734_24778174.1344608186754"
Date: Fri, 30 May 2025 14:16:26 +0000
Message-ID: {msg_id}
------=_Part_4200734_24778174.1344608186754
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: quoted-printable

Thanks for the update. Please go ahead !

--
Your Dear Customer
------=_Part_4200734_24778174.1344608186754
Content-Type: text/html; charset=utf-8
Content-Transfer-Encoding: quoted-printable

<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
 <head>=20
  <meta http-equiv=3D"Content-Type" content=3D"text/html; charset=3Dutf-8" />
 </head>=20
 <body style=3D"background: #ffffff;-webkit-text-size-adjust: 100%;">=20

  <p>Thanks for the update. Please go ahead !</p>

  <p>--<br/>
     Your Dear Customer
  <p>
 </body>
</html>
------=_Part_4200734_24778174.1344608186754--
"""


class TestCustomerResponse(HttpCaseWithUserPortal):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.helpdesk_team1 = cls.env.ref("helpdesk_mgmt.helpdesk_team_1")
        cls.stage_new = cls.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_new")
        cls.stage_in_progress = cls.env.ref(
            "helpdesk_mgmt.helpdesk_ticket_stage_in_progress"
        )
        cls.stage_done = cls.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_done")
        cls.helpdesk_team1.update(
            {
                "autoupdate_ticket_stage": True,
                "autopupdate_src_stage_ids": [(4, cls.stage_in_progress.id)],
                "autopupdate_dest_stage_id": cls.stage_done.id,
            }
        )
        # Plain partner with no Odoo user account (used for Branch 3/4 tests)
        cls.external_partner = cls.env["res.partner"].create(
            {
                "name": "External Customer",
                "email": "external@example.com",
            }
        )

    def _create_ticket(self, team, partner):
        ticket = self.env["helpdesk.ticket"].create(
            [
                {
                    "name": f"Ticket ({team.name})",
                    "description": "Description",
                    "team_id": team.id,
                    "partner_id": partner.id,
                    "priority": "1",
                }
            ]
        )
        return ticket

    def message_process(self):
        MailThread = self.env["mail.thread"]
        message = MAIL_TEMPLATE.format(
            to=self.env.user.email,
            subject="Your ticket has been created !!",
            email_from=self.partner_portal.email,
            msg_id="168242744424.20.2028152230359369389@dd607af32154",
        )
        MailThread.message_process(
            model="helpdesk.ticket",
            message=message,
            save_original=False,
            strip_attachments=True,
            thread_id=self.ticket.id,
        )

    def _message_process_from(self, email_from):
        """Simulate an incoming email from an arbitrary address."""
        MailThread = self.env["mail.thread"]
        message = MAIL_TEMPLATE.format(
            to=self.env.user.email,
            subject="Customer reply",
            email_from=email_from,
            msg_id=f"<test-{abs(hash(email_from))}@example.com>",
        )
        MailThread.message_process(
            model="helpdesk.ticket",
            message=message,
            save_original=False,
            strip_attachments=True,
            thread_id=self.ticket.id,
        )

    def test_change_stage_customer_answered(self):
        self.ticket_id = self._create_ticket(self.helpdesk_team1, self.partner_portal)
        self.ticket_id.stage_id = self.stage_in_progress
        self.ticket_id.with_user(self.user_portal).message_post(body="Test message")
        self.assertEqual(self.ticket_id.stage_id, self.stage_done)

    def test_no_change_stage_customer_answered(self):
        self.ticket_id = self._create_ticket(self.helpdesk_team1, self.partner_portal)
        self.ticket_id.with_user(self.user_portal).message_post(body="Test message")
        self.assertEqual(self.ticket_id.stage_id, self.stage_new)

    def test_change_stage_deactivated(self):
        self.helpdesk_team1.autoupdate_ticket_stage = False
        self.ticket_id = self._create_ticket(self.helpdesk_team1, self.partner_portal)
        self.ticket_id.with_user(self.user_portal).message_post(body="Test message")
        self.assertEqual(self.ticket_id.stage_id, self.stage_new)

    def test_change_stage_customer_answered_through_mail(self):
        self.ticket = self._create_ticket(self.helpdesk_team1, self.partner_portal)
        self.ticket.stage_id = self.stage_in_progress
        self.message_process()
        self.assertEqual(self.ticket.stage_id, self.stage_done)

    def test_no_change_stage_customer_answered_through_mail(self):
        self.ticket = self._create_ticket(self.helpdesk_team1, self.partner_portal)
        self.message_process()
        self.assertEqual(self.ticket.stage_id, self.stage_new)

    def test_change_stage_deactivated_through_mail(self):
        self.helpdesk_team1.autoupdate_ticket_stage = False
        self.ticket = self._create_ticket(self.helpdesk_team1, self.partner_portal)
        self.message_process()
        self.assertEqual(self.ticket.stage_id, self.stage_new)

    def test_change_stage_partner_email_not_normalized(self):
        """Stage must update even when the stored partner email has different casing."""
        # Temporarily store email in non-normalized form on the partner
        original_email = self.partner_portal.email
        self.partner_portal.email = original_email.upper()
        self.ticket = self._create_ticket(self.helpdesk_team1, self.partner_portal)
        self.ticket.stage_id = self.stage_in_progress
        try:
            self.message_process()
            self.assertEqual(self.ticket.stage_id, self.stage_done)
        finally:
            self.partner_portal.email = original_email

    def test_change_stage_partner_email_field_only(self):
        """Stage must update when ticket has partner_email but no partner_id."""
        self.ticket = self._create_ticket(self.helpdesk_team1, self.partner_portal)
        self.ticket.stage_id = self.stage_in_progress
        partner_email = self.partner_portal.email
        # Detach partner_id but keep partner_email
        self.ticket.write({"partner_id": False, "partner_email": partner_email})
        self.message_process()
        self.assertEqual(self.ticket.stage_id, self.stage_done)

    # ------------------------------------------------------------------
    # Branch 1 negative: a *different* known Odoo user sends the reply
    # ------------------------------------------------------------------

    def test_no_change_stage_branch1_wrong_known_sender(self):
        """Branch 1: Both sender and ticket have known partners but they differ.

        The stage must NOT change when an Odoo user who is not the ticket
        partner posts a reply via email.
        """
        self.ticket = self._create_ticket(self.helpdesk_team1, self.partner_portal)
        self.ticket.stage_id = self.stage_in_progress
        # Send the email as the internal admin user (different partner)
        original_ticket = self.ticket
        MailThread = self.env["mail.thread"]
        message = MAIL_TEMPLATE.format(
            to=self.env.user.email,
            subject="Internal reply",
            email_from=self.env.user.email,
            msg_id="<branch1-neg-test@example.com>",
        )
        MailThread.message_process(
            model="helpdesk.ticket",
            message=message,
            save_original=False,
            strip_attachments=True,
            thread_id=original_ticket.id,
        )
        self.assertEqual(original_ticket.stage_id, self.stage_in_progress)

    # ------------------------------------------------------------------
    # Branch 3: external sender (no Odoo user), ticket has partner_id
    # ------------------------------------------------------------------

    def test_change_stage_branch3_external_sender_matches(self):
        """Branch 3: External sender's email matches the ticket partner email.

        Because the sender has no Odoo user account, user_id is not set and
        email_partner is False.  The code must fall back to comparing the
        normalised ticket partner email against the normalised email_from.
        """
        self.ticket = self._create_ticket(self.helpdesk_team1, self.external_partner)
        self.ticket.stage_id = self.stage_in_progress
        self._message_process_from("external@example.com")
        self.assertEqual(self.ticket.stage_id, self.stage_done)

    def test_change_stage_branch3_external_sender_normalization(self):
        """Branch 3: email_normalize is applied to the stored partner email.

        Even when the partner's email is stored in mixed case the stage must
        update because both sides are normalised before comparison.  The old
        code used a plain string comparison and would have missed this case.
        """
        original_email = self.external_partner.email
        self.external_partner.email = original_email.upper()
        self.ticket = self._create_ticket(self.helpdesk_team1, self.external_partner)
        self.ticket.stage_id = self.stage_in_progress
        try:
            self._message_process_from("external@example.com")
            self.assertEqual(self.ticket.stage_id, self.stage_done)
        finally:
            self.external_partner.email = original_email

    def test_change_stage_branch3_external_sender_with_display_name(self):
        """Branch 3: incoming email_from uses the «"Name" <addr>» display format.

        email_normalize must strip the display name from the incoming address
        so that the comparison against the normalised ticket partner email
        still succeeds.  The old code compared the raw email_from string and
        would have missed this case.
        """
        self.ticket = self._create_ticket(self.helpdesk_team1, self.external_partner)
        self.ticket.stage_id = self.stage_in_progress
        self._message_process_from('"External Customer" <external@example.com>')
        self.assertEqual(self.ticket.stage_id, self.stage_done)

    def test_no_change_stage_branch3_external_sender_wrong_email(self):
        """Branch 3: External sender's email does not match the ticket partner.

        The stage must NOT change when the incoming address differs from the
        ticket partner's email.
        """
        self.ticket = self._create_ticket(self.helpdesk_team1, self.external_partner)
        self.ticket.stage_id = self.stage_in_progress
        self._message_process_from("wrong@example.com")
        self.assertEqual(self.ticket.stage_id, self.stage_in_progress)

    # ------------------------------------------------------------------
    # Branch 4: external sender (no Odoo user), ticket has only partner_email
    # ------------------------------------------------------------------

    def test_change_stage_branch4_no_partner_external_sender_matches(self):
        """Branch 4: No partner_id on ticket, external sender email matches.

        This branch was entirely absent from the old code.  Both email_partner
        and ticket_partner are False; the only available data are the raw
        partner_email field and the incoming email_from address.
        """
        self.ticket = self._create_ticket(self.helpdesk_team1, self.external_partner)
        self.ticket.stage_id = self.stage_in_progress
        self.ticket.write(
            {"partner_id": False, "partner_email": "external@example.com"}
        )
        self._message_process_from("external@example.com")
        self.assertEqual(self.ticket.stage_id, self.stage_done)

    def test_change_stage_branch4_external_sender_with_display_name(self):
        """Branch 4: incoming email_from uses the «"Name" <addr>» display format.

        No partner_id on the ticket, only partner_email is set.  email_normalize
        must strip the display name from the incoming address so that the
        comparison against the normalised ticket partner_email field still
        succeeds.
        """
        self.ticket = self._create_ticket(self.helpdesk_team1, self.external_partner)
        self.ticket.stage_id = self.stage_in_progress
        self.ticket.write(
            {"partner_id": False, "partner_email": "external@example.com"}
        )
        self._message_process_from('"External Customer" <external@example.com>')
        self.assertEqual(self.ticket.stage_id, self.stage_done)

    def test_no_change_stage_branch4_no_partner_external_sender_wrong_email(self):
        """Branch 4: No partner_id on ticket, external sender email does not match.

        The stage must NOT change when the incoming address differs from the
        ticket's partner_email field.
        """
        self.ticket = self._create_ticket(self.helpdesk_team1, self.external_partner)
        self.ticket.stage_id = self.stage_in_progress
        self.ticket.write(
            {"partner_id": False, "partner_email": "external@example.com"}
        )
        self._message_process_from("wrong@example.com")

    def test_no_crash_when_assigning_mail_to_new_thread(self):
        """New thread (thread_id=None) must not crash and creates the ticket."""
        MailThread = self.env["mail.thread"]
        message = MAIL_TEMPLATE.format(
            to=self.env.user.email,
            subject="Brand new ticket via mail",
            email_from=self.external_partner.email,
            msg_id="<new-thread-assign-test@example.com>",
        )
        thread_id = MailThread.message_process(
            model="helpdesk.ticket",
            message=message,
            save_original=False,
            strip_attachments=True,
        )
        ticket = self.env["helpdesk.ticket"].browse(thread_id).exists()
        self.assertTrue(ticket)

    def test_change_ticket_status_via_mail_no_ticket_id(self):
        """Route without thread_id returns None instead of raising."""
        MailThread = self.env["mail.thread"]
        routes = [("helpdesk.ticket", None, {}, self.env.user.id, None)]
        result = MailThread.change_ticket_status_via_mail(
            routes, {"email_from": "external@example.com"}
        )
        self.assertIsNone(result)

    def test_skip_autoreply_default_returns_false(self):
        """Default hook returns False so normal stage updates are not suppressed."""
        mail_thread = self.env["mail.thread"]
        result = mail_thread._skip_ticket_stage_update_from_autoreply(None, {}, [])
        self.assertFalse(result)

    def test_no_stage_update_when_autoreply_skips(self):
        """When _skip_ticket_stage_update_from_autoreply returns True (e.g. an
        integration module detected an auto-reply), the stage must NOT be updated
        even though the mail would otherwise qualify for an update."""
        self.ticket = self._create_ticket(self.helpdesk_team1, self.partner_portal)
        self.ticket.stage_id = self.stage_in_progress
        MailThreadClass = type(self.env["mail.thread"])
        with patch.object(
            MailThreadClass,
            "_skip_ticket_stage_update_from_autoreply",
            return_value=True,
        ):
            self.message_process()
        self.assertEqual(self.ticket.stage_id, self.stage_in_progress)
