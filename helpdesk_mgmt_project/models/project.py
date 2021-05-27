from odoo import _, api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    ticket_ids = fields.One2many(
        comodel_name="helpdesk.ticket", inverse_name="project_id", string="Tickets"
    )
    ticket_count = fields.Integer(
        compute="_compute_ticket_count", string="Ticket Count", store=True
    )
    label_tickets = fields.Char(
        string="Use Tickets as",
        default=lambda s: _("Tickets"),
        translate=True,
        help="Gives label to tickets on project's kanban view.",
    )
    todo_ticket_count = fields.Integer(
        string="Number of tickets", compute="_compute_ticket_count", store=True
    )

    @api.depends("ticket_ids", "ticket_ids.stage_id")
    def _compute_ticket_count(self):
        for record in self:
            record.ticket_count = len(record.ticket_ids)
            record.todo_ticket_count = len(
                record.ticket_ids.filtered(lambda ticket: not ticket.closed)
            )
