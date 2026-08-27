# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HelpdeskTicketForm(models.Model):
    _name = "helpdesk.ticket.form"
    _description = "Helpdesk Portal Ticket Form"
    _order = "name"

    name = fields.Char(
        required=True,
        translate=True,
    )
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    intro = fields.Text(
        translate=True,
        help="Optional text shown above the questions in the portal form.",
    )
    question_ids = fields.One2many(
        comodel_name="helpdesk.ticket.form.question",
        inverse_name="form_id",
        string="Questions",
        copy=True,
    )
    question_count = fields.Integer(
        compute="_compute_question_count",
    )

    @api.depends("question_ids")
    def _compute_question_count(self):
        for record in self:
            record.question_count = len(record.question_ids)
