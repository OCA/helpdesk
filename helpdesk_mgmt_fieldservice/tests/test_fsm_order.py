# Copyright (C) 2022 Trevi Software
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime

from odoo.exceptions import ValidationError

from . import common


class TestFSMOrder(common.TestHelpdeskFieldservice):
    def test_view_order_action(self):

        order = self.create_order(ticket=self.ticket)
        res = self.ticket.fsm_order_ids[0].action_view_order()

        self.assertEqual(
            res["res_model"], "fsm.order", "The view action is for model fsm.order"
        )
        self.assertEqual(res["views"][0][1], "form", "The view type is 'form'")
        self.assertEqual(
            res["res_id"],
            order.id,
            "The view action contains the record id of my order",
        )

    def test_order_action_complete(self):

        order = self.create_order(ticket=self.ticket)

        # date_end is False
        with self.assertRaises(ValidationError):
            self.ticket.fsm_order_ids[0].action_complete()

        order.date_end = datetime.today()
        # resolution is False
        with self.assertRaises(ValidationError):
            self.ticket.fsm_order_ids[0].action_complete()

        order.resolution = "foo"
        res = self.ticket.fsm_order_ids[0].action_complete()

        self.assertTrue(order.stage_id.is_closed, "The order is closed/completed")
        self.assertEqual(
            res["res_model"],
            "fsm.order.close.wizard",
            "When no other open orders exist, the ticket close wizard is launched",
        )

        order2 = self.create_order(ticket=self.ticket)
        res = order.action_complete()
        self.assertTrue(
            res,
            "When open orders exist closing one does not run the ticket close wizard",
        )

        order2.date_end = datetime.today()
        order2.resolution = "bar"
        order2.write({"stage_id": self.fsm_completed.id, "is_button": True})
        self.ticket.stage_id = self.done_stage
        res = order2.action_complete()
        self.assertTrue(
            res, "Completing an order for an already closed ticket does nothing"
        )
