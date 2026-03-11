# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestHelpdeskTicketAccountMove(TransactionCase):
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
        cls.account_move_1 = cls.env["account.move"].create(
            {
                "partner_id": cls.partner.id,
                "ticket_ids": [Command.set([cls.ticket.id])],
            }
        )
        cls.account_move_2 = cls.env["account.move"].create(
            {
                "partner_id": cls.partner.id,
                "ticket_ids": [Command.set([cls.ticket.id])],
            }
        )

    def test_account_moves_associated_with_ticket(self):
        # Verify that a Helpdesk ticket has multiple account moves associated with it.
        self.assertEqual(len(self.ticket.account_move_ids), 2)
        self.assertIn(self.account_move_1, self.ticket.account_move_ids)
        self.assertIn(self.account_move_2, self.ticket.account_move_ids)

    def test_partner_association_in_account_move(self):
        # Verify that an account move is associated with the correct ticket partner.
        self.assertEqual(self.account_move_1.partner_id, self.partner)
        self.assertEqual(self.account_move_2.partner_id, self.partner)

    def test_smartbutton_account_move_count(self):
        # Check the account move counter in the smartbutton of the ticket.
        self.ticket._compute_account_move_count()
        self.assertEqual(self.ticket.account_move_count, 2)

    def test_action_view_account_moves(self):
        # Verify that the smartbutton action displays the associated account moves correctly.
        action = self.ticket.action_view_account_moves()
        self.assertEqual(action["domain"], [("ticket_ids", "in", [self.ticket.id])])
        self.assertDictEqual(
            action["context"],
            {
                "default_ticket_ids": [Command.link(self.ticket.id)],
                "default_partner_id": self.ticket.partner_id.id,
            },
        )

    def test_action_view_helpdesk_tickets(self):
        action = self.account_move_1.action_view_helpdesk_tickets()
        self.assertEqual(
            action["domain"], [("account_move_ids", "in", [self.account_move_1.id])]
        )
        self.assertDictEqual(
            action["context"],
            {
                "default_account_move_ids": [Command.set(self.account_move_1.ids)],
                "default_account_move_count": 1,
            },
        )
