# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestHelpdeskTicketEquipment(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        # Create test data
        cls.partner = cls.env["res.partner"].create({"name": "Partner 1"})
        cls.user_demo = cls.env.ref("base.user_demo")

        cls.location = cls.env.ref("fieldservice.location_1")

        cls.equipment = cls.env["fsm.equipment"].create(
            {
                "name": "Test Equipment",
                "location_id": cls.location.id,
            }
        )
        cls.equipment_no_location = cls.env["fsm.equipment"].create(
            {
                "name": "Test Equipment No Location",
            }
        )

        cls.team_id = cls.env["helpdesk.ticket.team"].create({"name": "Team Test"})

        cls.ticket = cls.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "Ticket test",
                "user_id": cls.user_demo.id,
                "team_id": cls.team_id.id,
                "fsm_location_id": cls.location.id,
            }
        )

    def test_01_equipment_assignment_invalid_location(self):
        """Test that equipment with different location raises validation error"""
        other_location = self.env.ref("fieldservice.test_location")

        equipment_other_location = self.env["fsm.equipment"].create(
            {
                "name": "Equipment Other Location",
                "location_id": other_location.id,
            }
        )

        with self.assertRaisesRegex(
            ValidationError,
            "The location of the ticket and equipment are not the same.",
        ):
            self.ticket.equipment_id = equipment_other_location
