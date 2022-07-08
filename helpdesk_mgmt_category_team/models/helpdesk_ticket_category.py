from odoo import fields, models


class HelpdeskTicketCategory(models.Model):
    _inherit = "helpdesk.ticket.category"

    team_id = fields.Many2one("helpdesk.ticket.team", string="Team")
