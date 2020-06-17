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
        cls.picking1 = cls.env.ref("stock.incomming_shipment1")
        cls.coupon_program_id = cls.env.ref("sale_coupon.10_percent_coupon")
        cls.ticket = helpdesk_ticket.create(
            {"name": "Test 1", "description": "Ticket test"}
        )
        cls.team_id = helpdesk_ticket_team.create({"name": "Team 1"})
        cls.ticket_with_sale_order = helpdesk_ticket.create(
            {
                "name": "Test 2",
                "description": "Ticket test with sale order",
                "sale_order_id": cls.sale_order_1.id,
                "partner_id": cls.sale_order_1.partner_id.id,
            }
        )
        cls.ticket_with_pickings = helpdesk_ticket.create(
            {
                "name": "Test 3",
                "description": "Ticket with pickings",
                "picking_ids": [(4, cls.picking1.id)],
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

        # Test picking_id
        self.assertFalse(self.ticket.picking_ids.ids)

        self.ticket.picking_ids = [(4, self.picking1.id)]

        self.assertEqual(
            self.env["stock.picking"]
            .search([("id", "in", self.ticket.picking_ids.ids)])
            .id,
            self.picking1.id,
        )

        self.assertEqual(
            self.ticket_with_pickings.picking_ids.ids, self.ticket.picking_ids.ids
        )

        self.ticket_with_pickings.picking_ids = None
        self.assertFalse(self.ticket_with_pickings.picking_ids.ids)

    def test_coupon_wizard(self):
        coupon_obj = self.env["sale.coupon.wizard"]
        self.ticket_with_sale_order.coupon_ids = [(5)]
        self.assertTrue(len(self.ticket_with_sale_order.coupon_ids), 0)
        values = {
            "ticket_id": self.ticket_with_sale_order.id,
            "partner_id": self.ticket_with_sale_order.partner_id.id,
            "sale_order_id": self.ticket_with_sale_order.sale_order_id.id,
            "program_id": self.coupon_program_id.id,
        }
        coupon_wizard_id = coupon_obj.create(values)
        i = 5
        for _ in range(0, i + 1):
            coupon_wizard_id.action_create_coupon()
        self.assertTrue(len(self.ticket_with_sale_order.coupon_ids), i)
