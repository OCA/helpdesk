# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HelpdeskTicketFormAnswer(models.Model):
    _name = "helpdesk.ticket.form.answer"
    _description = "Helpdesk Portal Ticket Form Answer Choice"
    _order = "question_id, sequence, id"

    question_id = fields.Many2one(
        comodel_name="helpdesk.ticket.form.question",
        string="Question",
        required=True,
        ondelete="cascade",
        index=True,
    )
    sequence = fields.Integer(default=10)
    name = fields.Char(
        string="Choice",
        required=True,
        translate=True,
    )
