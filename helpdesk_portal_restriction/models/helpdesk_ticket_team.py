from odoo import fields, models


class HelpdeskTicketTeam(models.Model):
    _inherit = "helpdesk.ticket.team"

    helpdesk_partner_ids = fields.Many2many(
        "res.partner", "helpdesk_team_ids", string="Partners"
    )
