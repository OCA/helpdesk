from odoo import _, api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    ticket_ids = fields.One2many(
        comodel_name="helpdesk.ticket", inverse_name="project_id", string="Tickets"
    )
    ticket_count = fields.Integer(compute="_compute_ticket_count", store=True)
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
        HelpdeskTicket = self.env["helpdesk.ticket"]
        domain = [("project_id", "in", self.ids)]
        fields = ["project_id"]
        groupby = ["project_id"]
        counts = {
            pr["project_id"][0]: pr["project_id_count"]
            for pr in HelpdeskTicket.read_group(domain, fields, groupby)
        }
        domain.append(("closed", "=", False))
        counts_todo = {
            pr["project_id"][0]: pr["project_id_count"]
            for pr in HelpdeskTicket.read_group(domain, fields, groupby)
        }
        for record in self:
            record.ticket_count = counts.get(record.id, 0)
            record.todo_ticket_count = counts_todo.get(record.id, 0)
