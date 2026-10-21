from odoo import Command, api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    ticket_ids = fields.Many2many("helpdesk.ticket")
    ticket_count = fields.Integer(
        string="Tickets Count", compute="_compute_ticket_count"
    )

    @api.depends("ticket_ids")
    def _compute_ticket_count(self):
        group_data = self.env["helpdesk.ticket"]._read_group(
            domain=[("sale_order_ids", "in", self.ids)],
            groupby=["sale_order_ids"],
            aggregates=["__count"],
        )
        mapped_data = {order.id: count for (order, count) in group_data}
        for order in self:
            order.ticket_count = mapped_data.get(order.id, 0)

    def action_create_helpdesk_ticket(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Create Helpdesk ticket",
            "res_model": "helpdesk.ticket",
            "view_mode": "form",
            "view_id": self.env.ref("helpdesk_mgmt.ticket_view_form").id,
            "target": "new",
            "context": {
                "default_partner_id": self.partner_id.id,
                "default_name": self.name,
                "default_origin": self.name,
                "default_sale_order_ids": [Command.link(self.id)],
                "from_sale_order": True,
            },
        }
