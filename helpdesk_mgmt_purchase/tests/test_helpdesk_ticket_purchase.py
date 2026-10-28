# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestHelpdeskTicketPurchase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        cls.purchase_order_1 = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner.id,
                "ticket_ids": [Command.set([cls.ticket.id])],
            }
        )
        cls.purchase_order_2 = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner.id,
                "ticket_ids": [Command.set([cls.ticket.id])],
            }
        )

    def test_purchase_orders_associated_with_ticket(self):
        self.assertEqual(len(self.ticket.purchase_order_ids), 2)
        self.assertIn(self.purchase_order_1, self.ticket.purchase_order_ids)
        self.assertIn(self.purchase_order_2, self.ticket.purchase_order_ids)

    def test_partner_association_in_purchase_order(self):
        self.assertEqual(self.purchase_order_1.partner_id, self.partner)
        self.assertEqual(self.purchase_order_2.partner_id, self.partner)

    def test_smartbuttons_count(self):
        self.assertEqual(self.ticket.po_count, 2)
        self.assertEqual(self.purchase_order_1.ticket_count, 1)
        self.assertEqual(self.purchase_order_2.ticket_count, 1)

    def test_action_view_purchase_orders(self):
        """Test action view behaves correctly depending on the number of linked POs."""
        # Scenario 1: Multiple POs linked -> List view
        action_multiple = self.ticket.action_view_purchase_orders()
        self.assertEqual(action_multiple["view_mode"], "tree,form")
        self.assertIn(
            ("id", "in", self.ticket.purchase_order_ids.ids),
            action_multiple["domain"],
        )

        # Scenario 2: Single PO linked -> Form view
        single_ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Single PO Ticket",
                "partner_id": self.partner.id,
                "description": "test",
            }
        )
        po_single = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "ticket_ids": [Command.set([single_ticket.id])],
            }
        )

        action_single = single_ticket.action_view_purchase_orders()
        self.assertEqual(action_single["view_mode"], "form")
        self.assertEqual(action_single["res_id"], po_single.id)

    def test_action_view_helpdesk_tickets(self):
        """Test action view behaves correctly depending on the number of linked tickets."""
        # Scenario 1: Single ticket linked -> Form view
        action_single = self.purchase_order_1.action_view_helpdesk_tickets()
        self.assertEqual(action_single["view_mode"], "form")
        self.assertEqual(action_single["res_id"], self.ticket.id)

        # Scenario 2: Multiple tickets linked -> List view
        ticket_2 = self.env["helpdesk.ticket"].create(
            {
                "name": "Second Helpdesk Ticket",
                "partner_id": self.partner.id,
                "description": "test",
            }
        )
        po_multiple = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "ticket_ids": [Command.set([self.ticket.id, ticket_2.id])],
            }
        )

        action_multiple = po_multiple.action_view_helpdesk_tickets()
        self.assertEqual(action_multiple["view_mode"], "tree,form")
        self.assertIn(
            ("id", "in", po_multiple.ticket_ids.ids),
            action_multiple["domain"],
        )
