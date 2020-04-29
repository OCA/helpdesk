from odoo import fields, models


class HelpdeskTicketTeam(models.Model):
    _inherit = "helpdesk.ticket.team"

    assign_sale_order = fields.Boolean(
        string="Assign sale order",
        default=False,
        help="""
        Given a ticket from this team,
        allows assigning a past sale order the customer has
        """,
    )
