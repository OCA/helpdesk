# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import Datetime
from odoo.tests import common


class TestHelpdeskTicketGrn(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.carrier = cls.env["res.partner"].create(
            {
                "name": "Test Carrier",
            }
        )
        cls.grn = cls.env["stock.grn"].create(
            {
                "date": Datetime.now(),
                "delivery_note_supplier_number": "SUPP-TEST",
                "carrier_id": cls.carrier.id,
            }
        )
        cls.picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.env.ref("stock.picking_type_in").id,
                "location_id": cls.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": cls.env.ref("stock.stock_location_stock").id,
                "grn_id": cls.grn.id,
            }
        )

    def test_grn_related_fields(self):
        """Test that helpdesk ticket correctly pulls data from GRN via Picking."""
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "stock_picking_id": self.picking.id,
                "description": "Test description",
            }
        )

        self.assertEqual(ticket.grn_id, self.grn, "GRN ID was not pulled correctly.")
        self.assertEqual(ticket.grn_date, self.grn.date, "GRN Date does not match.")
        self.assertEqual(
            ticket.delivery_note_supplier_number,
            self.grn.delivery_note_supplier_number,
            "Supplier delivery note number does not match.",
        )

    def test_grn_change_propagation(self):
        """Test that changing the GRN on the picking updates the ticket."""
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Update Ticket",
                "stock_picking_id": self.picking.id,
                "description": "Test description again",
            }
        )

        new_grn = self.env["stock.grn"].create(
            {
                "delivery_note_supplier_number": "SUPP-TEST-2",
                "carrier_id": self.carrier.id,
            }
        )
        self.picking.grn_id = new_grn
        self.assertEqual(ticket.delivery_note_supplier_number, "SUPP-TEST-2")
