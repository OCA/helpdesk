# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class HelpdeskFormCommon(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = cls.env["helpdesk.ticket.form"].create({"name": "Hardware issue"})
        cls.q_text = cls.env["helpdesk.ticket.form.question"].create(
            {
                "form_id": cls.form.id,
                "name": "Describe the issue",
                "question_type": "text",
                "sequence": 1,
            }
        )
        cls.q_sev = cls.env["helpdesk.ticket.form.question"].create(
            {
                "form_id": cls.form.id,
                "name": "Severity",
                "question_type": "selection",
                "sequence": 2,
                "answer_ids": [
                    (0, 0, {"name": "Low"}),
                    (0, 0, {"name": "High"}),
                    (0, 0, {"name": "Critical"}),
                ],
            }
        )
        cls.sev_high = cls.q_sev.answer_ids.filtered(lambda a: a.name == "High")
        cls.sev_critical = cls.q_sev.answer_ids.filtered(lambda a: a.name == "Critical")
        # Conditional: shown only when Severity is High or Critical.
        cls.q_when = cls.env["helpdesk.ticket.form.question"].create(
            {
                "form_id": cls.form.id,
                "name": "When did it start?",
                "question_type": "char",
                "sequence": 3,
                "required": True,
                "is_conditional": True,
                "triggering_question_id": cls.q_sev.id,
                "triggering_answer_ids": [
                    (6, 0, (cls.sev_high | cls.sev_critical).ids)
                ],
            }
        )
