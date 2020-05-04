from odoo.tests import common


class TestHelpdeskSalesOrder(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestHelpdeskSalesOrder, cls).setUpClass()
        helpdesk_ticket = cls.env["helpdesk.ticket"]
        helpdesk_ticket_team = cls.env["helpdesk.ticket.team"]
        cls.user_admin = cls.env.ref("base.user_root")
        cls.sale_order_1 = cls.env.ref("sale.sale_order_1")
        cls.sale_order_2 = cls.env.ref("sale.sale_order_2")
        cls.ticket = helpdesk_ticket.create(
            {"name": "Test 1", "description": "Ticket test"}
        )
        cls.team_id = helpdesk_ticket_team.create({"name": "Team 1"})
        cls.ticket_with_sale_order = helpdesk_ticket.create(
            {
                "name": "Test 2",
                "description": "Ticket test with sale order",
                "sale_order_id": cls.sale_order_1.id,
            }
        )

    def test_getters(self):
        self.ticket.assign_sale_order = True
        self.ticket_with_sale_order.assign_sale_order = True
        self.assertTrue(self.ticket.assign_sale_order)
        self.assertTrue(self.ticket_with_sale_order.assign_sale_order)

        # First, check that the ticket has no sale order
        self.assertFalse(self.ticket.sale_order_id.id)

        # Second, assign the first sale order to the ticket
        # and check that the operation was done successfully
        # variable equal check and database equal search
        self.ticket.sale_order_id = self.sale_order_1.id
        self.assertEqual(
            self.ticket.sale_order_id.id, self.sale_order_1.id,
        )
        self.assertEqual(
            self.env["helpdesk.ticket"].browse([self.ticket.id]).sale_order_id.id,
            self.sale_order_1.id,
        )

        self.assertEqual(
            self.ticket_with_sale_order.sale_order_id.id, self.sale_order_1.id
        )

        self.ticket_with_sale_order.sale_order_id = self.sale_order_2.id
        self.assertEqual(
            self.ticket_with_sale_order.sale_order_id.id, self.sale_order_2.id,
        )

        self.ticket_with_sale_order.sale_order_id = None
        self.assertFalse(self.ticket_with_sale_order.sale_order_id.id)
