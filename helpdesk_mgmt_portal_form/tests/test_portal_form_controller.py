# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from werkzeug.datastructures import MultiDict

from odoo.addons.helpdesk_mgmt_portal_form.controllers.main import (
    HelpdeskTicketFormController,
)

from .common import HelpdeskFormCommon


class TestPortalFormController(HelpdeskFormCommon):
    """Exercise the pure controller logic (no HTTP request context needed)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.controller = HelpdeskTicketFormController()

    def _field(self, question):
        return f"answer_{question.id}"

    def _active(self, data):
        md = MultiDict()
        for key, value in data:
            md.add(key, value)
        questions = self.controller._get_active_questions(self.form, md)
        return questions.mapped("name")

    def test_answer_values_char(self):
        md = MultiDict([(self._field(self.q_text), "Broken screen")])
        self.assertEqual(
            self.controller._get_answer_values(self.q_text, md), ["Broken screen"]
        )

    def test_answer_values_missing(self):
        self.assertEqual(
            self.controller._get_answer_values(self.q_text, MultiDict()), []
        )

    def test_answer_values_multi(self):
        q_multi = self.env["helpdesk.ticket.form.question"].create(
            {
                "form_id": self.form.id,
                "name": "Parts",
                "question_type": "multi",
                "answer_ids": [(0, 0, {"name": "Screen"}), (0, 0, {"name": "Battery"})],
            }
        )
        md = MultiDict(
            [(self._field(q_multi), "Screen"), (self._field(q_multi), "Battery")]
        )
        self.assertEqual(
            self.controller._get_answer_values(q_multi, md), ["Screen", "Battery"]
        )

    def test_answer_values_boolean(self):
        q_bool = self.env["helpdesk.ticket.form.question"].create(
            {"form_id": self.form.id, "name": "Warranty?", "question_type": "boolean"}
        )
        self.assertEqual(
            self.controller._get_answer_values(
                q_bool, MultiDict([(self._field(q_bool), "1")])
            ),
            ["Yes"],
        )
        self.assertEqual(
            self.controller._get_answer_values(q_bool, MultiDict()), ["No"]
        )

    def test_conditional_choice_subset(self):
        # q_when is triggered by Severity in {High, Critical}.
        self.assertNotIn("When did it start?", self._active([]))
        self.assertNotIn(
            "When did it start?", self._active([(self._field(self.q_sev), "Low")])
        )
        self.assertIn(
            "When did it start?", self._active([(self._field(self.q_sev), "High")])
        )
        self.assertIn(
            "When did it start?", self._active([(self._field(self.q_sev), "Critical")])
        )

    def test_conditional_boolean_trigger(self):
        q_bool = self.env["helpdesk.ticket.form.question"].create(
            {
                "form_id": self.form.id,
                "name": "Warranty?",
                "question_type": "boolean",
                "sequence": 10,
            }
        )
        self.env["helpdesk.ticket.form.question"].create(
            {
                "form_id": self.form.id,
                "name": "Purchase date",
                "question_type": "char",
                "sequence": 11,
                "is_conditional": True,
                "triggering_question_id": q_bool.id,
                "triggering_bool_value": "yes",
            }
        )
        self.assertIn("Purchase date", self._active([(self._field(q_bool), "1")]))
        self.assertNotIn("Purchase date", self._active([]))

    def test_conditional_chain(self):
        # A two-level chain: a flag shown only for Severity=High, and a
        # follow-up shown only when that flag is answered "Yes".
        q_flag = self.env["helpdesk.ticket.form.question"].create(
            {
                "form_id": self.form.id,
                "name": "Reproducible?",
                "question_type": "selection",
                "sequence": 20,
                "is_conditional": True,
                "triggering_question_id": self.q_sev.id,
                "triggering_answer_ids": [(6, 0, self.sev_high.ids)],
                "answer_ids": [(0, 0, {"name": "Yes"}), (0, 0, {"name": "No"})],
            }
        )
        self.env["helpdesk.ticket.form.question"].create(
            {
                "form_id": self.form.id,
                "name": "Steps to reproduce",
                "question_type": "text",
                "sequence": 21,
                "is_conditional": True,
                "triggering_question_id": q_flag.id,
                "triggering_answer_ids": [
                    (6, 0, q_flag.answer_ids.filtered(lambda a: a.name == "Yes").ids)
                ],
            }
        )
        # Severity=Low: neither the flag nor its dependent are shown.
        names = self._active([(self._field(self.q_sev), "Low")])
        self.assertNotIn("Reproducible?", names)
        self.assertNotIn("Steps to reproduce", names)
        # Severity=High + flag=Yes: the whole chain is shown.
        names = self._active(
            [(self._field(self.q_sev), "High"), (self._field(q_flag), "Yes")]
        )
        self.assertIn("Reproducible?", names)
        self.assertIn("Steps to reproduce", names)
        # Severity=High but flag=No: dependent stays hidden (cascade).
        names = self._active(
            [(self._field(self.q_sev), "High"), (self._field(q_flag), "No")]
        )
        self.assertIn("Reproducible?", names)
        self.assertNotIn("Steps to reproduce", names)

    def test_submitted_answers_only_active(self):
        md = MultiDict(
            [
                (self._field(self.q_text), "Broken"),
                (self._field(self.q_sev), "Low"),
                # answer to the conditional question, which must be dropped
                (self._field(self.q_when), "Yesterday"),
            ]
        )
        # Patch the request-bound helper by calling the active resolution
        # directly; _get_submitted_answers relies on request.httprequest.form.
        answers = [
            {
                "label": q.name,
                "question_type": q.question_type,
                "values": self.controller._get_answer_values(q, md),
            }
            for q in self.controller._get_active_questions(self.form, md)
        ]
        labels = [a["label"] for a in answers]
        self.assertIn("Describe the issue", labels)
        self.assertIn("Severity", labels)
        self.assertNotIn("When did it start?", labels)
