from odoo import Command, api, fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    sale_order_ids = fields.Many2many("sale.order")
    so_count = fields.Integer(
        string="Sale Order Count", compute="_compute_so_count", store=True
    )

    @api.depends("sale_order_ids")
    def _compute_so_count(self):
        for ticket in self:
            ticket.so_count = len(ticket.sale_order_ids)

    def action_view_sale_orders(self):
        """Returns action to view sale orders related to this ticket."""
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        action["domain"] = [("ticket_ids", "in", [self.id])]
        action["context"] = {
            "default_ticket_ids": [Command.link([self.id])],
            "default_partner_id": self.partner_id.id,
        }
        return action
