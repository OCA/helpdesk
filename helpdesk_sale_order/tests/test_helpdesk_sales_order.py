from odoo.tests import common


class TestHelpdeskSalesOrder(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestHelpdeskSalesOrder, cls).setUpClass()
        helpdesk_ticket = cls.env["helpdesk.ticket"]
        cls.user_admin = cls.env.ref("base.user_root")
        cls.sale_order_1 = cls.env.ref("sale.sale_order_1")
        cls.sale_order_2 = cls.env.ref("sale.sale_order_1")
        cls.ticket = helpdesk_ticket.create(
            {"name": "Test 1", "description": "Ticket test"}
        )
        cls.ticket_with_sale_order = helpdesk_ticket.create(
            {
                "name": "Test 2",
                "description": "Ticket test with sale order",
                "sale_order_id": cls.sale_order_1.id
            }
        )

    def test_helpdesk_ticket_none_sale_order(self):
        self.assertFalse(self.ticket.sale_order_id.id)

        self.ticket.sale_order_id = self.sale_order_1.id

        self.assertIs(
            self.ticket.sale_order_id.id,
            self.sale_order_1.id,
        )

    def test_helpdesk_sale_order(self):
        self.assertIs(
            self.ticket_with_sale_order.sale_order_id.id,
            self.sale_order_1.id
        )

        self.ticket_with_sale_order.sale_order_id = self.sale_order_2.id

        self.assertIs(
            self.ticket_with_sale_order.sale_order_id.id,
            self.sale_order_2.id,
        )
