# Copyright 2024 Antoni Marroig(APSL-Nagarro)<amarroig@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json

from odoo import http

from odoo.addons.base.tests.common import HttpCaseWithUserPortal


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
            {
                "name": "Ticket (%s)" % (team.name),
                "description": "Description",
                "team_id": team.id,
                "partner_id": partner.id,
                "priority": "1",
            }
        )
        return ticket

    def _create_message_new(self, ticket):
        return self.url_open(
            url="/mail/chatter_post",
            data=json.dumps(
                {
                    "params": {
                        "res_model": "helpdesk.ticket",
                        "res_id": ticket.id,
                        "message": "Test message",
                        "csrf_token": http.Request.csrf_token(self),
                    },
                }
            ),
            headers={"Content-Type": "application/json"},
        )

    def test_change_stage_customer_answered(self):
        self.authenticate("portal", "portal")
        self.ticket_id = self._create_ticket(self.helpdesk_team1, self.partner_portal)
        self.ticket_id.stage_id = self.stage_in_progress
        res = self._create_message_new(self.ticket_id)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(self.ticket_id.stage_id, self.stage_done)

    def test_no_change_stage_customer_answered(self):
        self.authenticate("portal", "portal")
        self.ticket_id = self._create_ticket(self.helpdesk_team1, self.partner_portal)
        res = self._create_message_new(self.ticket_id)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(self.ticket_id.stage_id, self.stage_new)

    def test_change_stage_deactivated(self):
        self.authenticate("portal", "portal")
        self.helpdesk_team1.autoupdate_ticket_stage = False
        self.ticket_id = self._create_ticket(self.helpdesk_team1, self.partner_portal)
        res = self._create_message_new(self.ticket_id)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(self.ticket_id.stage_id, self.stage_new)
