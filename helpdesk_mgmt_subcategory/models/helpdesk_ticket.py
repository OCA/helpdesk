from odoo import fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    root_category_id = fields.Many2one(
        related='team_id.root_category_id'
    )