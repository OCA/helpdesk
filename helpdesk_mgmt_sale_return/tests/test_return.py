# Copyright 2021 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.tests import common


class TestHelpdeskTicketReturn(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        helpdesk_ticket = cls.env["helpdesk.ticket"]
        cls.user_admin = cls.env.ref("base.user_root")
        cls.user_demo = cls.env.ref("base.user_demo")
        cls.stage_in_progress = cls.env.ref(
            "helpdesk_mgmt.helpdesk_ticket_stage_in_progress"
        )

        cls.ticket = helpdesk_ticket.create(
            {"name": "Test 1", "description": "Ticket test"}
        )

    def test_helpdesk_return(self):
        self.ticket.sale_id = self.env.ref("sale_stock.sale_order_19")
        self.ticket.write(
            {
                "sale_line_ids": [
                    (
                        0,
                        0,
                        {
                            "sale_line_id": self.env.ref(
                                "sale_stock.sale_order_line_42"
                            ).id,
                            "qty": 2,
                        },
                    )
                ]
            }
        )
        self.ticket.return_sale_lines()
        self.assertEqual(self.ticket.stage_id, self.stage_in_progress)
        self.assertEqual(len(self.ticket.return_picking_ids), 1)
        self.assertEqual(len(self.ticket.return_picking_ids.move_line_ids), 1)
        self.assertEqual(
            self.ticket.return_picking_ids.move_line_ids.product_id,
            self.ticket.sale_line_ids.product_id,
        )
        self.assertEqual(
            self.ticket.return_picking_ids.move_line_ids.product_uom_qty,
            self.ticket.sale_line_ids.qty,
        )
        # Cancel return and recreate one (in case the customers fails to send package back)
        self.ticket.return_picking_ids.action_cancel()
        self.ticket.return_sale_lines()
        # Assert that only the OUT pickings are returned (do not return the return)
        self.assertEqual(len(self.ticket.return_picking_ids), 2)
