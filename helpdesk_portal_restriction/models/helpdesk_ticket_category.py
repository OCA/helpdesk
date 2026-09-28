from odoo import fields, models


class HelpdeskTicketCategory(models.Model):
    _inherit = "helpdesk.ticket.category"

    helpdesk_category_partner_ids = fields.Many2many(
        "res.partner", "helpdesk_category_ids", string="Partners"
    )
