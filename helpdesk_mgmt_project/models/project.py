from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    ticket_ids = fields.One2many(
        comodel_name="helpdesk.ticket", inverse_name="project_id", string="Tickets"
    )
    ticket_count = fields.Integer(compute="_compute_ticket_count", store=True)
    label_tickets = fields.Char(
        string="Use Tickets as",
        default=lambda self: self.env._("Tickets"),
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
