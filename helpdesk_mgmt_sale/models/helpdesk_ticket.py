from odoo import _, api, fields, models


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
            "default_ticket_ids": [(4, [self.id])],
            "default_partner_id": self.partner_id.id,
        }
        return action

    @api.model_create_multi
    def create(self, vals_list):
        tickets = super().create(vals_list)
        if self.env.context.get("from_sale_order"):
            # only one ticket is possible here
            for sale in tickets.sale_order_ids:
                sale.message_post(body=self._get_default_message_creation(tickets))

        return tickets

    def _get_default_message_creation(self, tickets):
        return _(
            f"Helpdesk Ticket {tickets.display_name} created by {self.env.user.name}"
        )
