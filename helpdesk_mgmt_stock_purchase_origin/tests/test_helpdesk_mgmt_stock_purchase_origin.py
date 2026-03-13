# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestHelpdeskMgmtStockOrigin(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        product = cls.env["product.product"].create({"name": "Test Product"})

        vendor = cls.env["res.partner"].create({"name": "Test Vendor"})
        cls.po = cls.env["purchase.order"].create(
            {
                "partner_id": vendor.id,
                "order_line": [Command.create({"product_id": product.id})],
            }
        )
        cls.po.button_confirm()
        cls.in_pick = cls.po.picking_ids

    def test_action_view_helpdesk_tickets_in_picking(self):
        action = self.in_pick.action_view_helpdesk_tickets()
        self.assertEqual(
            action["context"].get("default_purchase_order_ids"),
            [Command.set(self.po.ids)],
        )
