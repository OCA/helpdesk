# Copyright 2024 Antoni Marroig(APSL-Nagarro)<amarroig@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

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
