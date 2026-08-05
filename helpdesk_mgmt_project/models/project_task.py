from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    ticket_ids = fields.One2many(
        comodel_name="helpdesk.ticket", inverse_name="task_id", string="Tickets"
    )
    ticket_count = fields.Integer(compute="_compute_ticket_count")
    label_tickets = fields.Char(
        related="project_id.label_tickets",
    )
    todo_ticket_count = fields.Integer(
        string="Number of tickets", compute="_compute_ticket_count"
    )

    @api.depends("ticket_ids", "ticket_ids.stage_id")
    def _compute_ticket_count(self):
        HelpdeskTicket = self.env["helpdesk.ticket"]
        domain = [("task_id", "in", self.ids)]
        counts = {
            task.id: count
            for task, count in HelpdeskTicket._read_group(
                domain, ["task_id"], ["__count"]
            )
        }
        counts_todo = {
            task.id: count
            for task, count in HelpdeskTicket._read_group(
                domain + [("closed", "=", False)], ["task_id"], ["__count"]
            )
        }
        for record in self:
            record.ticket_count = counts.get(record.id, 0)
            record.todo_ticket_count = counts_todo.get(record.id, 0)

    def action_view_ticket(self):
        self.ensure_one()
        return self.ticket_ids._get_records_action(
            name=self.label_tickets,
            view_mode="kanban,list,form",
            context={"default_task_id": self.id},
        )
