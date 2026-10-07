# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.tests.common import tagged

from odoo.addons.base.tests.common import (
    DISABLED_MAIL_CONTEXT,
    HttpCaseWithUserPortal,
)


@tagged("post_install", "-at_install")
class TestPortalFormHttp(HttpCaseWithUserPortal):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.company = cls.env.ref("base.main_company")
        cls.company.helpdesk_mgmt_portal_select_category = True
        cls.partner_portal.parent_id = cls.company.partner_id
        cls.form = cls.env["helpdesk.ticket.form"].create({"name": "Portal form"})
        cls.q_desc = cls.env["helpdesk.ticket.form.question"].create(
            {
                "form_id": cls.form.id,
                "name": "What is broken?",
                "question_type": "char",
                "sequence": 1,
            }
        )
        cls.q_sev = cls.env["helpdesk.ticket.form.question"].create(
            {
                "form_id": cls.form.id,
                "name": "Severity",
                "question_type": "selection",
                "sequence": 2,
                "answer_ids": [(0, 0, {"name": "Low"}), (0, 0, {"name": "High"})],
            }
        )
        cls.sev_high = cls.q_sev.answer_ids.filtered(lambda a: a.name == "High")
        cls.q_when = cls.env["helpdesk.ticket.form.question"].create(
            {
                "form_id": cls.form.id,
                "name": "When did it start?",
                "question_type": "char",
                "sequence": 3,
                "is_conditional": True,
                "triggering_question_id": cls.q_sev.id,
                "triggering_answer_ids": [(6, 0, cls.sev_high.ids)],
            }
        )
        cls.category_form = cls.env["helpdesk.ticket.category"].create(
            {
                "name": "With form",
                "company_id": cls.company.id,
                "show_in_portal": True,
                "form_id": cls.form.id,
            }
        )
        cls.category_plain = cls.env["helpdesk.ticket.category"].create(
            {
                "name": "Without form",
                "company_id": cls.company.id,
                "show_in_portal": True,
            }
        )
        cls.category_hidden = cls.env["helpdesk.ticket.category"].create(
            {
                "name": "Not in portal",
                "company_id": cls.company.id,
                "show_in_portal": False,
                "form_id": cls.form.id,
            }
        )

    def _get_ticket(self, subject):
        return self.env["helpdesk.ticket"].search([("name", "=", subject)], limit=1)

    def test_route_returns_fragment(self):
        self.authenticate("portal", "portal")
        resp = self.url_open(f"/ticket/form/{self.category_form.id}")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("What is broken?", resp.text)
        self.assertIn('data-conditional="1"', resp.text)

    def test_route_empty_without_form(self):
        self.authenticate("portal", "portal")
        resp = self.url_open(f"/ticket/form/{self.category_plain.id}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.text.strip(), "")

    def test_route_empty_for_hidden_category(self):
        # A category not shown in the portal must never serve its form.
        self.authenticate("portal", "portal")
        resp = self.url_open(f"/ticket/form/{self.category_hidden.id}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.text.strip(), "")

    def _submit(self, category, subject, extra=None):
        data = {
            "category": category.id,
            "csrf_token": http.Request.csrf_token(self),
            "subject": subject,
            "description": "ignored when a form is used",
        }
        data.update(extra or {})
        resp = self.url_open("/submitted/ticket", data=data)
        self.assertEqual(resp.status_code, 200)

    def test_submit_builds_description_from_answers(self):
        self.authenticate("portal", "portal")
        subject = "form-ticket-low"
        self._submit(
            self.category_form,
            subject,
            {
                f"answer_{self.q_desc.id}": "The keyboard",
                f"answer_{self.q_sev.id}": "Low",
                # Answer to the conditional question that must be dropped since
                # Severity is Low (its trigger is not matched).
                f"answer_{self.q_when.id}": "Should not appear",
            },
        )
        ticket = self._get_ticket(subject)
        self.assertTrue(ticket)
        self.assertIn("What is broken?", ticket.description)
        self.assertIn("The keyboard", ticket.description)
        self.assertIn("Severity", ticket.description)
        self.assertNotIn("When did it start?", ticket.description)
        self.assertNotIn("Should not appear", ticket.description)

    def test_submit_keeps_matched_conditional(self):
        self.authenticate("portal", "portal")
        subject = "form-ticket-high"
        self._submit(
            self.category_form,
            subject,
            {
                f"answer_{self.q_desc.id}": "The screen",
                f"answer_{self.q_sev.id}": "High",
                f"answer_{self.q_when.id}": "Yesterday",
            },
        )
        ticket = self._get_ticket(subject)
        self.assertIn("When did it start?", ticket.description)
        self.assertIn("Yesterday", ticket.description)

    def test_submit_without_form_uses_free_text(self):
        self.authenticate("portal", "portal")
        subject = "plain-ticket"
        self._submit(
            self.category_plain, subject, {"description": "Plain free-text body"}
        )
        ticket = self._get_ticket(subject)
        self.assertIn("Plain free-text body", ticket.description)
