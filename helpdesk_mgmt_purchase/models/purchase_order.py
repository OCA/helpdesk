# Copyright 2017 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, _, api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    ticket_ids = fields.Many2many("helpdesk.ticket")
    ticket_count = fields.Integer(
        string="Tickets Count", compute="_compute_ticket_count", store=True
    )

    @api.depends("ticket_ids")
    def _compute_ticket_count(self):
        ticket_data = self.env["helpdesk.ticket"].read_group(
            [("purchase_order_ids", "in", self.ids)],
            ["purchase_order_ids"],
            ["purchase_order_ids"],
        )
        mapped_data = {
            data["purchase_order_ids"][0]: data["purchase_order_ids_count"]
            for data in ticket_data
        }
        for order in self:
            order.ticket_count = mapped_data.get(order.id, 0)

    def action_view_helpdesk_tickets(self):
        self.ensure_one()

        action = {
            "name": _("Tickets"),
            "type": "ir.actions.act_window",
            "res_model": "helpdesk.ticket",
            "target": "current",
            "context": {
                "default_purchase_order_ids": [Command.set(self.ids)],
            },
        }

        if self.ticket_count == 1:
            action.update(
                {
                    "view_mode": "form",
                    "res_id": self.ticket_ids.ids[0],
                }
            )
        else:
            action.update(
                {
                    "view_mode": "tree,form",
                    "domain": [("id", "in", self.ticket_ids.ids)],
                }
            )

        return action
