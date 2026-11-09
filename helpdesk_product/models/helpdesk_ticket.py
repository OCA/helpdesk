from odoo import fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    product_id = fields.Many2one(
        comodel_name="product.product",
        domain=[("ticket_active", "=", True)],
    )
