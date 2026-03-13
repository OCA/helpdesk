# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_view_helpdesk_tickets(self):
        action = super().action_view_helpdesk_tickets()

        picking_type_code = self.picking_type_id.code
        if picking_type_code == "outgoing" and self.origin:
            origin_so_data = self.env["sale.order"].search_read(
                domain=[("name", "=", self.origin)], fields=["id"], limit=1
            )
            if origin_so_data:
                action["context"].update(
                    {
                        "default_sale_order_ids": [
                            Command.set([origin_so_data[0].get("id")])
                        ]
                    }
                )
        return action
