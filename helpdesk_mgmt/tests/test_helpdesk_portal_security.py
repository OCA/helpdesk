# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import hashlib
from unittest.mock import patch

from odoo.http import request

from odoo.addons.helpdesk_mgmt.controllers.main import HelpdeskTicketController

from .test_helpdesk_portal import TestHelpdeskPortalBase


class TestHelpdeskPortalSecurity(TestHelpdeskPortalBase):
    def _close(self, ticket, stage, **kwargs):
        return self.url_open(
            "/ticket/close",
            data={
                "ticket_id": ticket.id,
                "stage_id": stage.id,
                "csrf_token": self.csrf_token(),
            },
            allow_redirects=False,
            **kwargs,
        )

    def _submit(self, **values):
        data = {
            "csrf_token": self.csrf_token(),
            "subject": "forged submission",
            "description": "forged",
        }
        data.update(**values)
        return self.url_open("/submitted/ticket", data=data, allow_redirects=False)

    def _forged_tickets(self):
        return self.env["helpdesk.ticket"].search([("name", "=", "forged submission")])

    def test_cannot_close_unrelated_ticket(self):
        partner = self.env["res.partner"].create({"name": "Unrelated tenant"})
        ticket = self._create_ticket(partner, "unrelated maintenance request")
        previous_stage = ticket.stage_id
        self.assertFalse(ticket.with_user(self.user_portal).has_access("read"))
        self.authenticate("portal", "portal")
        stage = self.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_done")
        self.assertEqual(self._close(ticket, stage).status_code, 404)
        ticket.invalidate_recordset()
        self.assertEqual(ticket.stage_id, previous_stage)

    def test_cannot_close_ticket_in_another_company(self):
        company = self.env["res.company"].create({"name": "Other lessor"})
        ticket = self._create_ticket(
            self.partner_portal, "other company ticket", company_id=company.id
        )
        previous_stage = ticket.stage_id
        self.authenticate("portal", "portal")
        stage = self.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_done")
        self.assertEqual(self._close(ticket, stage).status_code, 404)
        ticket.invalidate_recordset()
        self.assertEqual(ticket.stage_id, previous_stage)

    def test_cannot_reclose_an_already_closed_ticket(self):
        """A forged POST must not restage a closed ticket nor restamp closed_date."""
        done = self.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_done")
        cancelled = self.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_cancelled")
        self.portal_ticket.stage_id = done
        closed_date = self.portal_ticket.closed_date
        self.assertTrue(closed_date)
        self.authenticate("portal", "portal")
        self.assertEqual(self._close(self.portal_ticket, cancelled).status_code, 302)
        self.portal_ticket.invalidate_recordset()
        self.assertEqual(self.portal_ticket.stage_id, done)
        self.assertEqual(self.portal_ticket.closed_date, closed_date)

    def test_submit_rejects_non_numeric_ids(self):
        self.company.helpdesk_mgmt_portal_select_team = True
        self.authenticate("portal", "portal")
        for values in (
            {"category": "abc"},
            {"category": self.portal_category.id, "team": "abc"},
        ):
            self.assertEqual(self._submit(**values).status_code, 400)
        self.assertFalse(self._forged_tickets())

    def test_submit_rejects_records_hidden_from_portal(self):
        self.company.helpdesk_mgmt_portal_select_team = True
        hidden = {"company_id": self.company.id, "show_in_portal": False}
        category = self.env["helpdesk.ticket.category"].create(
            dict(hidden, name="Internal only category")
        )
        team = self.env["helpdesk.ticket.team"].create(
            dict(hidden, name="Internal only team")
        )
        self.authenticate("portal", "portal")
        self.assertEqual(self._submit(category=category.id).status_code, 403)
        self.assertEqual(
            self._submit(category=self.portal_category.id, team=team.id).status_code,
            403,
        )
        self.assertFalse(self._forged_tickets())

    def test_submit_honours_a_narrowed_category_list(self):
        """Narrowing ``_get_categories`` must restrict the POST too."""
        offered_id = self.portal_category.id
        not_offered = self.env["helpdesk.ticket.category"].create(
            {
                "name": "Hidden by the override",
                "company_id": self.company.id,
                "show_in_portal": True,
            }
        )
        self.authenticate("portal", "portal")
        with patch.object(
            HelpdeskTicketController,
            "_get_categories",
            lambda controller, **kw: request.env["helpdesk.ticket.category"].browse(
                offered_id
            ),
        ):
            self.assertEqual(self._submit(category=not_offered.id).status_code, 403)
            self.assertEqual(self._submit(category=offered_id).status_code, 302)
        tickets = self._forged_tickets()
        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets.category_id.id, offered_id)

    def test_cannot_choose_a_stage_from_another_team(self):
        team = self.env["helpdesk.ticket.team"].create({"name": "Other service team"})
        stage = self.env["helpdesk.ticket.stage"].create(
            {
                "name": "Other team done",
                "closed": True,
                "close_from_portal": True,
                "team_ids": [(6, 0, team.ids)],
            }
        )
        previous_stage = self.portal_ticket.stage_id
        self.authenticate("portal", "portal")
        self.assertEqual(self._close(self.portal_ticket, stage).status_code, 403)
        self.portal_ticket.invalidate_recordset()
        self.assertEqual(self.portal_ticket.stage_id, previous_stage)

    def test_close_rejects_get(self):
        self.authenticate("portal", "portal")
        stage = self.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_done")
        response = self.url_open(
            f"/ticket/close?ticket_id={self.portal_ticket.id}&stage_id={stage.id}",
            allow_redirects=False,
        )
        self.assertEqual(response.status_code, 405)
        self.assertFalse(self.portal_ticket.closed)

    def test_close_requires_csrf(self):
        self.authenticate("portal", "portal")
        stage = self.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_done")
        with self.assertLogs("odoo.http", level="WARNING") as captured:
            response = self.url_open(
                "/ticket/close",
                data={"ticket_id": self.portal_ticket.id, "stage_id": stage.id},
                allow_redirects=False,
            )
        self.assertIn("No CSRF validation token", " ".join(captured.output))
        self.assertEqual(response.status_code, 400)
        self.assertFalse(self.portal_ticket.closed)

    def test_attachment_upload_keeps_original_bytes(self):
        payload = b"Maintenance photo placeholder: kitchen leak.\n"
        self.authenticate("portal", "portal")
        response = self.url_open(
            "/submitted/ticket",
            data={
                "category": self.portal_category.id,
                "csrf_token": self.csrf_token(),
                "subject": "Uploaded repair evidence",
                "description": "Leaking sink",
            },
            files={"attachment": ("repair.txt", payload, "text/plain")},
        )
        self.assertEqual(response.status_code, 200)
        ticket = self.env["helpdesk.ticket"].search(
            [("name", "=", "Uploaded repair evidence")]
        )
        self.assertEqual(len(ticket), 1)
        attachment = ticket.attachment_ids
        self.assertEqual(len(attachment), 1)
        self.assertEqual(attachment.file_size, len(payload))
        self.assertEqual(attachment.raw.content, payload)
        self.assertEqual(attachment.checksum, hashlib.sha1(payload).hexdigest())
        self.assertIn("repair.txt", response.text)

    def test_cannot_download_unrelated_attachment(self):
        partner = self.env["res.partner"].create({"name": "Unrelated attachment owner"})
        ticket = self._create_ticket(partner, "private ticket")
        attachment = self.env["ir.attachment"].create(
            {
                "name": "private.txt",
                "raw": b"private request details",
                "res_model": "helpdesk.ticket",
                "res_id": ticket.id,
            }
        )
        self.authenticate("portal", "portal")
        response = self.url_open(
            f"/web/content/{attachment.id}?download=true", allow_redirects=False
        )
        self.assertIn(response.status_code, (403, 404))
        self.assertNotIn(b"private request details", response.content)
