# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json

from odoo.exceptions import ValidationError
from odoo.tests import Form

from .common import HelpdeskFormCommon


class TestHelpdeskTicketForm(HelpdeskFormCommon):
    def test_question_count(self):
        self.assertEqual(self.form.question_count, 3)
        self.env["helpdesk.ticket.form.question"].create(
            {"form_id": self.form.id, "name": "Extra", "question_type": "char"}
        )
        self.assertEqual(self.form.question_count, 4)

    def test_triggering_values_choice(self):
        self.assertEqual(
            sorted(self.q_when._get_triggering_values()), ["Critical", "High"]
        )
        self.assertEqual(
            json.loads(self.q_when.triggering_values_json),
            self.q_when._get_triggering_values(),
        )

    def test_triggering_values_boolean(self):
        q_bool = self.env["helpdesk.ticket.form.question"].create(
            {"form_id": self.form.id, "name": "Warranty?", "question_type": "boolean"}
        )
        q_cond = self.env["helpdesk.ticket.form.question"].create(
            {
                "form_id": self.form.id,
                "name": "Purchase date",
                "question_type": "char",
                "is_conditional": True,
                "triggering_question_id": q_bool.id,
                "triggering_bool_value": "yes",
            }
        )
        self.assertEqual(q_cond._get_triggering_values(), ["Yes"])
        q_cond.triggering_bool_value = "no"
        self.assertEqual(q_cond._get_triggering_values(), ["No"])

    def test_triggering_values_non_conditional(self):
        self.assertEqual(self.q_sev._get_triggering_values(), [])

    def test_constraint_missing_trigger(self):
        with self.assertRaises(ValidationError):
            self.env["helpdesk.ticket.form.question"].create(
                {
                    "form_id": self.form.id,
                    "name": "Orphan",
                    "question_type": "char",
                    "is_conditional": True,
                }
            )

    def test_constraint_self_dependency(self):
        with self.assertRaises(ValidationError):
            self.q_when.triggering_question_id = self.q_when

    def test_constraint_trigger_other_form(self):
        other_form = self.env["helpdesk.ticket.form"].create({"name": "Other"})
        other_q = self.env["helpdesk.ticket.form.question"].create(
            {
                "form_id": other_form.id,
                "name": "Other choice",
                "question_type": "selection",
                "answer_ids": [(0, 0, {"name": "X"})],
            }
        )
        with self.assertRaises(ValidationError):
            self.q_when.write(
                {
                    "triggering_question_id": other_q.id,
                    "triggering_answer_ids": [(6, 0, other_q.answer_ids.ids)],
                }
            )

    def test_constraint_boolean_without_value(self):
        q_bool = self.env["helpdesk.ticket.form.question"].create(
            {"form_id": self.form.id, "name": "Warranty?", "question_type": "boolean"}
        )
        with self.assertRaises(ValidationError):
            self.env["helpdesk.ticket.form.question"].create(
                {
                    "form_id": self.form.id,
                    "name": "Needs bool value",
                    "question_type": "char",
                    "is_conditional": True,
                    "triggering_question_id": q_bool.id,
                }
            )

    def test_constraint_trigger_wrong_type(self):
        with self.assertRaises(ValidationError):
            self.env["helpdesk.ticket.form.question"].create(
                {
                    "form_id": self.form.id,
                    "name": "Bad trigger",
                    "question_type": "char",
                    "is_conditional": True,
                    "triggering_question_id": self.q_text.id,
                }
            )

    def test_constraint_choice_without_answers(self):
        with self.assertRaises(ValidationError):
            self.env["helpdesk.ticket.form.question"].create(
                {
                    "form_id": self.form.id,
                    "name": "Needs answers",
                    "question_type": "char",
                    "is_conditional": True,
                    "triggering_question_id": self.q_sev.id,
                }
            )

    def test_constraint_answer_of_other_question(self):
        q_other = self.env["helpdesk.ticket.form.question"].create(
            {
                "form_id": self.form.id,
                "name": "Colour",
                "question_type": "selection",
                "answer_ids": [(0, 0, {"name": "Blue"})],
            }
        )
        with self.assertRaises(ValidationError):
            self.q_when.triggering_answer_ids = q_other.answer_ids

    def test_onchange_is_conditional_clears_trigger(self):
        with Form(self.q_when) as question:
            question.is_conditional = False
        self.assertFalse(self.q_when.triggering_question_id)
        self.assertFalse(self.q_when.triggering_answer_ids)

    def test_onchange_type_clears_answers(self):
        standalone = self.env["helpdesk.ticket.form.question"].create(
            {
                "form_id": self.form.id,
                "name": "Colour",
                "question_type": "selection",
                "answer_ids": [(0, 0, {"name": "Blue"})],
            }
        )
        with Form(standalone) as question:
            question.question_type = "char"
        self.assertFalse(standalone.answer_ids)
