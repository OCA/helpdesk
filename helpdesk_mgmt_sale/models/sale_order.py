from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    ticket_id = fields.Many2one("helpdesk.ticket")
