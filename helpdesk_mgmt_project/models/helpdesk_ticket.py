from odoo import api, fields, models


class HelpdeskTicket(models.Model):

    _inherit = "helpdesk.ticket"

    project_id = fields.Many2one(string="Project", comodel_name="project.project")
    task_id = fields.Many2one(
        string="Task",
        comodel_name="project.task",
        compute="_compute_task_id",
        readonly=False,
        store=True,
    )

    @api.depends("project_id")
    def _compute_task_id(self):
        for record in self:
            record.task_id = False
