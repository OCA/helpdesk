# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestHelpdeskMgmtStockOrigin(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        product = cls.env["product.product"].create({"name": "Test Product"})

        customer = cls.env["res.partner"].create({"name": "Test Customer"})
        cls.so = cls.env["sale.order"].create(
            {
                "partner_id": customer.id,
                "order_line": [Command.create({"product_id": product.id})],
            }
        )
        cls.so.action_confirm()
        cls.out_pick = cls.so.picking_ids

    def test_action_view_helpdesk_tickets_out_picking(self):
        action = self.out_pick.action_view_helpdesk_tickets()
        self.assertEqual(
            action["context"].get("default_sale_order_ids"), [Command.set(self.so.ids)]
        )
