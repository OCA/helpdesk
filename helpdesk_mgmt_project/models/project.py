from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    ticket_ids = fields.One2many(
        comodel_name="helpdesk.ticket", inverse_name="project_id", string="Tickets"
    )
    ticket_count = fields.Integer(compute="_compute_ticket_count")
    label_tickets = fields.Char(
        string="Use Tickets as",
        default=lambda self: self.env._("Tickets"),
        translate=True,
        help="Gives label to tickets on project's kanban view.",
    )
    todo_ticket_count = fields.Integer(
        string="Number of tickets", compute="_compute_ticket_count"
    )

    @api.depends("ticket_ids", "ticket_ids.stage_id")
    def _compute_ticket_count(self):
        HelpdeskTicket = self.env["helpdesk.ticket"]
        domain = [("project_id", "in", self.ids)]
        counts = {
            project.id: count
            for project, count in HelpdeskTicket._read_group(
                domain, ["project_id"], ["__count"]
            )
        }
        counts_todo = {
            project.id: count
            for project, count in HelpdeskTicket._read_group(
                domain + [("closed", "=", False)], ["project_id"], ["__count"]
            )
        }
        for record in self:
            record.ticket_count = counts.get(record.id, 0)
            record.todo_ticket_count = counts_todo.get(record.id, 0)

    def _get_stat_buttons(self):
        buttons = super()._get_stat_buttons()
        if self.env.user.has_group("helpdesk_mgmt.group_helpdesk_user_own"):
            buttons.append(
                {
                    "icon": "life-ring",
                    "text": self.env._("Tickets"),
                    "number": self.ticket_count,
                    "action_type": "object",
                    "action": "action_open_helpdesk_tickets",
                    "show": self.ticket_count > 0,
                    "sequence": 4,
                }
            )
        return buttons

    def action_open_helpdesk_tickets(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "helpdesk_mgmt_project.ticket_action_from_project"
        )
        action["domain"] = [("project_id", "=", self.id)]
        action["context"] = {
            "default_project_id": self.id,
        }
        return action
