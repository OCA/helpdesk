from odoo import fields, models


class HelpdeskTeam(models.Model):
    _inherit = "helpdesk.ticket.team"

    default_project_id = fields.Many2one(
        comodel_name="project.project",
        string="Project",
        readonly=False,
        company_dependent=True,
    )
