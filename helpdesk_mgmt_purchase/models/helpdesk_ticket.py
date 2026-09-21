# Copyright 2017 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, _, api, fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    purchase_order_ids = fields.Many2many("purchase.order")
    po_count = fields.Integer(
        string="Purchase Order Count", compute="_compute_po_count", store=True
    )

    @api.depends("purchase_order_ids")
    def _compute_po_count(self):
        purchase_data = self.env["purchase.order"].read_group(
            [("ticket_ids", "in", self.ids)], ["ticket_ids"], ["ticket_ids"]
        )
        mapped_data = {
            data["ticket_ids"][0]: data["ticket_ids_count"] for data in purchase_data
        }
        for ticket in self:
            ticket.po_count = mapped_data.get(ticket.id, 0)

    def action_view_purchase_orders(self):
        self.ensure_one()

        action = {
            "name": _("Purchase Orders"),
            "type": "ir.actions.act_window",
            "res_model": "purchase.order",
            "target": "current",
            "context": {
                "default_ticket_ids": [Command.set(self.ids)],
                "default_partner_id": self.partner_id.id,
            },
        }

        if self.po_count == 1:
            action.update(
                {
                    "view_mode": "form",
                    "res_id": self.purchase_order_ids.ids[0],
                }
            )
        else:
            action.update(
                {
                    "view_mode": "tree,form",
                    "domain": [("id", "in", self.purchase_order_ids.ids)],
                }
            )

        return action
