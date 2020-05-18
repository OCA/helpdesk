from odoo import fields, models


class HelpdeskTicket(models.Model):

    _inherit = "helpdesk.ticket"

    project_id = fields.Many2one(
        string='Project',
        comodel_name='project.project'
    )
