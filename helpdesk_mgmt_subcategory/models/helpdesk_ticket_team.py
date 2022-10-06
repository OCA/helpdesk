from odoo import fields, models


class HelpdeskTicketTeam(models.Model):

    _inherit = "helpdesk.ticket.team"

    root_category_id = fields.Many2one(
        string="Root Category",
        comodel_name="helpdesk.ticket.category",
        help="Default parent category for tickets i this team",
    )
