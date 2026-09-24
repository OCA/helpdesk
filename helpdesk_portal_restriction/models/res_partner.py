from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    helpdesk_team_ids = fields.Many2many(
        "helpdesk.ticket.team",
        "helpdesk_partner_ids",
        string="Available teams",
        required=True,
    )

    helpdesk_category_ids = fields.Many2many(
        "helpdesk.ticket.category",
        "helpdesk_category_partner_ids",
        string="Available category",
    )
