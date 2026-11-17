# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json

from odoo import api, fields, models
from odoo.exceptions import ValidationError

QUESTION_TYPES_WITH_OPTIONS = ("selection", "multi")
# Question types whose answer can drive the display of another question.
TRIGGER_QUESTION_TYPES = ("selection", "multi", "boolean")


class HelpdeskTicketFormQuestion(models.Model):
    _name = "helpdesk.ticket.form.question"
    _description = "Helpdesk Portal Ticket Form Question"
    _order = "form_id, sequence, id"

    form_id = fields.Many2one(
        comodel_name="helpdesk.ticket.form",
        string="Form",
        required=True,
        ondelete="cascade",
        index=True,
    )
    sequence = fields.Integer(default=10)
    name = fields.Char(
        string="Question",
        required=True,
        translate=True,
    )
    question_type = fields.Selection(
        selection=[
            ("char", "Single line text"),
            ("text", "Multi line text"),
            ("selection", "Single choice"),
            ("multi", "Multiple choice"),
            ("boolean", "Boolean"),
        ],
        string="Type",
        required=True,
        default="char",
    )
    required = fields.Boolean(
        help="The customer must answer this question. For a Yes / No question, "
        "it means the box must be ticked (answered Yes) to submit.",
    )
    help_text = fields.Char(
        translate=True,
        help="Optional hint displayed under the question in the portal form.",
    )
    placeholder = fields.Char(
        translate=True,
    )
    answer_ids = fields.One2many(
        comodel_name="helpdesk.ticket.form.answer",
        inverse_name="question_id",
        string="Choices",
        copy=True,
    )
    company_id = fields.Many2one(
        related="form_id.company_id",
        store=True,
    )
    is_conditional = fields.Boolean(
        string="Conditional display",
        help="Show this question only when another question is answered a "
        "specific way.",
    )
    triggering_question_id = fields.Many2one(
        comodel_name="helpdesk.ticket.form.question",
        string="Triggering question",
        ondelete="cascade",
        help="Single choice, multiple choice or Yes / No question whose answer "
        "controls the display of this one.",
    )
    triggering_question_type = fields.Selection(
        related="triggering_question_id.question_type",
        string="Triggering question type",
    )
    triggering_answer_ids = fields.Many2many(
        comodel_name="helpdesk.ticket.form.answer",
        string="Triggering answers",
        help="This question is shown when the triggering question is answered "
        "with any of these choices.",
    )
    triggering_bool_value = fields.Selection(
        selection=[("yes", "Yes"), ("no", "No")],
        string="Triggering value",
        help="This question is shown when the triggering Yes / No question has "
        "this value.",
    )
    triggering_values_json = fields.Char(
        compute="_compute_triggering_values_json",
        help="Technical: the matching values passed to the portal form.",
    )

    @api.depends(
        "is_conditional",
        "triggering_question_id.question_type",
        "triggering_answer_ids.name",
        "triggering_bool_value",
    )
    def _compute_triggering_values_json(self):
        for question in self:
            question.triggering_values_json = json.dumps(
                question._get_triggering_values()
            )

    def _get_triggering_values(self):
        """Return the answer values (as submitted) that reveal this question."""
        self.ensure_one()
        if not self.is_conditional or not self.triggering_question_id:
            return []
        if self.triggering_question_id.question_type == "boolean":
            if self.triggering_bool_value == "yes":
                return ["Yes"]
            if self.triggering_bool_value == "no":
                return ["No"]
            return []
        return self.triggering_answer_ids.mapped("name")

    @api.onchange("question_type")
    def _onchange_question_type(self):
        if self.question_type not in QUESTION_TYPES_WITH_OPTIONS:
            self.answer_ids = [fields.Command.clear()]

    @api.onchange("is_conditional")
    def _onchange_is_conditional(self):
        if not self.is_conditional:
            self.triggering_question_id = False
            self.triggering_answer_ids = [fields.Command.clear()]
            self.triggering_bool_value = False

    @api.onchange("triggering_question_id")
    def _onchange_triggering_question_id(self):
        stale = self.triggering_answer_ids.filtered(
            lambda answer: answer.question_id != self.triggering_question_id
        )
        if stale:
            self.triggering_answer_ids -= stale
        if self.triggering_question_type != "boolean":
            self.triggering_bool_value = False

    @api.constrains(
        "is_conditional",
        "triggering_question_id",
        "triggering_answer_ids",
        "triggering_bool_value",
    )
    def _check_conditional(self):
        for question in self:
            if not question.is_conditional:
                continue
            trigger = question.triggering_question_id
            if not trigger:
                raise ValidationError(
                    self.env._(
                        "Conditional question '%s' needs a triggering question.",
                        question.name,
                    )
                )
            if trigger == question:
                raise ValidationError(self.env._("A question cannot depend on itself."))
            if trigger.form_id != question.form_id:
                raise ValidationError(
                    self.env._("The triggering question must belong to the same form.")
                )
            if trigger.question_type not in TRIGGER_QUESTION_TYPES:
                raise ValidationError(
                    self.env._(
                        "The triggering question must be a single choice, "
                        "multiple choice or Yes / No question."
                    )
                )
            if trigger.question_type == "boolean":
                if not question.triggering_bool_value:
                    raise ValidationError(
                        self.env._(
                            "Conditional question '%s' needs a Yes / No "
                            "triggering value.",
                            question.name,
                        )
                    )
            elif not question.triggering_answer_ids:
                raise ValidationError(
                    self.env._(
                        "Conditional question '%s' needs at least one "
                        "triggering answer.",
                        question.name,
                    )
                )
            elif any(
                answer.question_id != trigger
                for answer in question.triggering_answer_ids
            ):
                raise ValidationError(
                    self.env._(
                        "The triggering answers must belong to the triggering question."
                    )
                )
