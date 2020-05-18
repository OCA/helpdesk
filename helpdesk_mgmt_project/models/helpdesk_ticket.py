from odoo import fields, models, api


class HelpdeskTicket(models.Model):

    _inherit = "helpdesk.ticket"

    project_id = fields.Many2one(
        string='Project',
        comodel_name='project.project'
    )
    task_id = fields.Many2one(
        string='Task',
        comodel_name='project.task'
    )

    @api.onchange('project_id')
    def _onchange_project(self):
        self.task_id = False
