# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestFSMEquipment(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create test data
        cls.location_partner_id = (
            cls.env["res.partner"].create({"name": "Loc Partner 1"}).id
        )

        cls.location = cls.env["fsm.location"].create(
            {
                "name": "Location 1",
                "partner_id": cls.location_partner_id,
                "owner_id": cls.location_partner_id,
            }
        )
        cls.equipment = cls.env["fsm.equipment"].create(
            {
                "name": "Test Equipment",
                "location_id": cls.location.id,
            }
        )

    def test_01_helpdesk_ticket_count_computation(self):
        """Test that helpdesk ticket count is computed correctly"""
        # Initially no tickets
        self.assertEqual(self.equipment.helpdesk_ticket_count, 0)

        # Create tickets and verify count
        ticket1 = self.env["helpdesk.ticket"].create(
            {
                "name": "Ticket 1",
                "equipment_id": self.equipment.id,
                "description": "Ticket test",
                "fsm_location_id": self.location.id,
            }
        )
        self.equipment.invalidate_recordset()
        self.assertEqual(self.equipment.helpdesk_ticket_count, 1)

        self.env["helpdesk.ticket"].create(
            {
                "name": "Ticket 2",
                "equipment_id": self.equipment.id,
                "description": "Ticket test",
                "fsm_location_id": self.location.id,
            }
        )
        self.equipment.invalidate_recordset()
        self.assertEqual(self.equipment.helpdesk_ticket_count, 2)

        # Remove a ticket and verify count
        ticket1.unlink()
        self.equipment.invalidate_recordset()
        self.assertEqual(self.equipment.helpdesk_ticket_count, 1)
