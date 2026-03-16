# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    def action_view_helpdesk_tickets(self):
        action = super().action_view_helpdesk_tickets()

        picking_type_code = self.picking_type_id.code
        if picking_type_code == "incoming" and self.origin:
            origin_po_data = self.env["purchase.order"].search_read(
                domain=[("name", "=", self.origin)], fields=["id"], limit=1
            )
            if origin_po_data:
                action["context"].update(
                    {
                        "default_purchase_order_ids": [
                            Command.set([origin_po_data[0].get("id")])
                        ]
                    }
                )

        return action
