from odoo import api, fields, models


class HelpdeskTicket(models.Model):

    _inherit = "helpdesk.ticket"

    @api.model
    def _default_company_id(self):
        if self._context.get("default_project_id"):
            return (
                self.env["project.project"]
                .browse(self._context["default_project_id"])
                .company_id
            )
        return self.env.company

    project_id = fields.Many2one(
        string="Project", comodel_name="project.project", check_company=True
    )
    task_id = fields.Many2one(
        string="Task",
        comodel_name="project.task",
        compute="_compute_task_id",
        readonly=False,
        store=True,
    )

    company_id = fields.Many2one(
        comodel_name="res.company",
        default=_default_company_id,
    )

    @api.depends("project_id")
    def _compute_task_id(self):
        for record in self:
            if record.task_id.project_id != record.project_id:
                record.task_id = False
