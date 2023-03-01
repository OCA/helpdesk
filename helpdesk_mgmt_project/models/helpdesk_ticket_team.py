from odoo import fields, models


class HelpdeskTeam(models.Model):
    _inherit = "helpdesk.ticket.team"

    default_project_id = fields.Many2one(
        "project.project", string="Project", readonly=False
    )
