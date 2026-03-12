# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    def action_view_helpdesk_tickets(self):
        action = super().action_view_helpdesk_tickets()

        picking_type_code = self.picking_type_id.code
        if picking_type_code == "incoming":
            origin_po = self.env["purchase.order"].search(
                [("name", "=", self.origin)], limit=1
            )
            action["context"].update(
                {"default_purchase_order_ids": [Command.set(origin_po.ids)]}
            )
        elif picking_type_code == "outgoing":
            origin_so = self.env["sale.order"].search(
                [("name", "=", self.origin)], limit=1
            )
            action["context"].update(
                {"default_sale_order_ids": [Command.set(origin_so.ids)]}
            )

        return action
