# Copyright (C) 2024 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.base.tests.common import BaseCommon


class TestHelpdeskTicketSale(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Ticket = cls.env["helpdesk.ticket"]
        cls.partner = cls.env["res.partner"].create(
            {"name": "Test Partner", "email": "testpartner@example.com"}
        )
        cls.ticket = cls.env["helpdesk.ticket"].create(
            {
                "name": "Test Helpdesk Ticket",
                "partner_id": cls.partner.id,
                "description": "Test Helpdesk Ticket",
            }
        )
        cls.sale_order_1 = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "ticket_ids": [(6, 0, [cls.ticket.id])],
            }
        )
        cls.sale_order_2 = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "ticket_ids": [(6, 0, [cls.ticket.id])],
            }
        )

    def test_sale_orders_associated_with_ticket(self):
        # Verify that a Helpdesk ticket has multiple sales orders associated with it.
        self.assertEqual(len(self.ticket.sale_order_ids), 2)
        self.assertIn(self.sale_order_1, self.ticket.sale_order_ids)
        self.assertIn(self.sale_order_2, self.ticket.sale_order_ids)

    def test_partner_association_in_sale_order(self):
        # Verify that a sales order is associated with the correct ticket partner.
        self.assertEqual(self.sale_order_1.partner_id, self.partner)
        self.assertEqual(self.sale_order_2.partner_id, self.partner)

    def test_smartbutton_sale_order_count(self):
        # Check the sales order counter in the smartbutton of the ticket.
        self.ticket._compute_so_count()
        self.assertEqual(self.ticket.so_count, 2)

    def test_action_view_sale_orders(self):
        # Verify that the smartbutton action displays the associated orders correctly.
        action = self.ticket.action_view_sale_orders()
        self.assertEqual(action["domain"], [("ticket_ids", "in", [self.ticket.id])])
        self.assertEqual(
            action["context"]["default_ticket_ids"], [(4, [self.ticket.id])]
        )

    def test_create_ticket_without_context(self):
        self.Ticket.create(
            {
                "name": "Test Ticket",
                "sale_order_ids": [(6, 0, [self.sale_order_1.id])],
                "description": "Test Helpdesk Ticket",
            }
        )
        messages = self.sale_order_1.message_ids.filtered(
            lambda m: "Helpdesk Ticket" in (m.body or "")
        )
        self.assertFalse(messages, "No message should be posted without context")

    def test_create_ticket_with_context(self):
        ticket = self.Ticket.with_context(from_sale_order=True).create(
            {
                "name": "Ticket Context",
                "sale_order_ids": [(6, 0, [self.sale_order_2.id])],
                "description": "Test Helpdesk Ticket",
            }
        )

        messages = self.sale_order_2.message_ids.filtered(
            lambda m: ticket.name in (m.body or "")
        )

        self.assertTrue(messages, "A message should be posted on the sale order")
        self.assertIn(self.env.user.name, messages[0].body)

    def test_action_context_values(self):
        action = self.sale_order_1.action_create_helpdesk_ticket()
        ctx = action["context"]

        self.assertEqual(ctx["default_partner_id"], self.partner.id)
        self.assertEqual(ctx["default_name"], self.sale_order_1.name)
        self.assertEqual(ctx["default_origin"], self.sale_order_1.name)
        self.assertEqual(ctx["default_sale_order_ids"], [(4, self.sale_order_1.id)])
        self.assertTrue(ctx["from_sale_order"])
