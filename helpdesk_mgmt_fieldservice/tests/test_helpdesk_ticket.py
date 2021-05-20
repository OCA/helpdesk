from odoo.tests import common


class TestHelpdeskTicket(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestHelpdeskTicket, cls).setUpClass()
        cls.HelpdeskTicket = cls.env["helpdesk.ticket"]
        cls.FsmOrder = cls.env["fsm.order"]
        cls.fsm_location = cls.env.ref("fieldservice.test_location")
        cls.ticket = cls.HelpdeskTicket.create(
            {
                "name": "Test 1",
                "description": "Ticket test",
            }
        )

    def test_helpdesk_ticket_all_orders_closed(self):
        self.assertFalse(
            self.ticket.all_orders_closed,
            "Helpdesk Ticket: with no linked FSM Order, "
            "all_orders_closed should be False",
        )

        order = self.FsmOrder.create(
            {
                "location_id": self.fsm_location.id,
                "ticket_id": self.ticket.id,
            }
        )

        self.assertFalse(
            order.stage_id.is_closed, "FSM Order: should be open by default"
        )
        self.assertFalse(
            self.ticket.all_orders_closed,
            "Helpdesk Ticket: with one FSM Order open, "
            "all_orders_closed should be False",
        )

        order.action_complete()
        self.assertTrue(order.stage_id.is_closed, "FSM Order: should be closed")
        self.assertTrue(
            self.ticket.all_orders_closed,
            "Helpdesk Ticket: with one FSM Order closed, "
            "all_orders_closed should be True",
        )

        order2 = self.FsmOrder.create(
            {
                "location_id": self.fsm_location.id,
                "ticket_id": self.ticket.id,
            }
        )
        self.assertFalse(
            self.ticket.all_orders_closed,
            "Helpdesk Ticket: with one FSM Order open and one closed, "
            "all_orders_closed should be False",
        )

        order2.stage_id.is_closed = True
        self.assertTrue(
            self.ticket.all_orders_closed,
            "Helpdesk Ticket: changing the attribute is_closed on the second order's "
            "stage, all_orders_closed should be recalculated to True",
        )
