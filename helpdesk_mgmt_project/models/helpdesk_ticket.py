from odoo import api, fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    project_id = fields.Many2one(
        string="Project", comodel_name="project.project", tracking=True
    )
    task_id = fields.Many2one(
        string="Task",
        comodel_name="project.task",
        compute="_compute_task_id",
        readonly=False,
        store=True,
        tracking=True,
    )
    milestone_id = fields.Many2one(
        "project.milestone",
        store=True,
        tracking=True,
        readonly=False,
        compute="_compute_milestone_id",
    )

    @api.depends("task_id")
    def _compute_milestone_id(self):
        for record in self:
            if record.task_id:
                record.milestone_id = record.task_id.milestone_id

    @api.depends("project_id")
    def _compute_task_id(self):
        for record in self:
            if record.task_id.project_id != record.project_id:
                record.task_id = False

    @api.model_create_multi
    def create(self, vals_list):
        tickets = super().create(vals_list)
        for ticket in tickets:
            if ticket.task_id and not ticket.task_id.project_id and ticket.project_id:
                ticket.task_id.project_id = ticket.project_id
        return tickets

    def write(self, vals):
        res = super().write(vals)
        if "task_id" in vals or "project_id" in vals:
            for ticket in self:
                if ticket.task_id and not ticket.task_id.project_id and ticket.project_id:
                    ticket.task_id.project_id = ticket.project_id
        return res
