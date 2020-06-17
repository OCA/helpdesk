from odoo import fields, models


class SaleCoupon(models.Model):
    _inherit = "sale.coupon"

    ticket_id = fields.Many2one(
        comodel_name="helpdesk.ticket", string="Ticket", required=False
    )
