from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    ticket_ids = fields.One2many(
        comodel_name="helpdesk.ticket", inverse_name="task_id", string="Tickets"
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
        result = self.env["ir.actions.act_window"]._for_xml_id(
            "helpdesk_mgmt.action_helpdesk_ticket_kanban_from_dashboard"
        )
        # choose the view_mode accordingly
        if not self.ticket_ids or self.ticket_count > 1:
            result["domain"] = f"[('id','in',{self.ticket_ids.ids})]"
            res = self.env.ref("helpdesk_mgmt.ticket_view_tree", False)
            tree_view = [(res and res.id or False, "tree")]
            if "views" in result:
                result["views"] = tree_view + [
                    (state, view) for state, view in result["views"] if view != "tree"
                ]
            else:
                result["views"] = tree_view
        elif self.ticket_count == 1:
            res = self.env.ref("helpdesk_mgmt.ticket_view_form", False)
            form_view = [(res and res.id or False, "form")]
            if "views" in result:
                result["views"] = form_view + [
                    (state, view) for state, view in result["views"] if view != "form"
                ]
            else:
                result["views"] = form_view
            result["res_id"] = self.ticket_ids.id
        return result
