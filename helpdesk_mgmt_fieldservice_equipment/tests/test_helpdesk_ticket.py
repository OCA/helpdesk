# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, new_test_user

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestHelpdeskTicketEquipment(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        # Create test data
        cls.partner = cls.env["res.partner"].create({"name": "Partner 1"})

        cls.user_demo = new_test_user(
            cls.env,
            email="emp@test.mycompany.com",
            groups="base.group_user,base.group_partner_manager",
            login="employee",
            name="Employee",
            password="employee",
        )

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
        test_loc_partner = self.env["res.partner"].create(
            {
                "name": "Test Loc Partner",
                "phone": "ABC",
                "email": "tlp@email.com",
            }
        )
        test_region = self.env["res.region"].create(
            {
                "name": "Test Region",
            }
        )
        test_district = self.env["res.district"].create(
            {
                "name": "Test District",
                "region_id": test_region.id,
            }
        )
        test_branch = self.env["res.branch"].create(
            {
                "name": "Test Branch",
                "district_id": test_district.id,
            }
        )
        test_territory = self.env["res.territory"].create(
            {
                "name": "Test Territory",
                "branch_id": test_branch.id,
            }
        )
        other_location = self.env["fsm.location"].create(
            {
                "name": "Test Location",
                "phone": "1234567890",
                "email": "tp@email.com",
                "partner_id": test_loc_partner.id,
                "owner_id": test_loc_partner.id,
                "territory_id": test_territory.id,
                "branch_id": test_branch.id,
                "district_id": test_district.id,
                "region_id": test_region.id,
                "direction": "Test Direction",
                "street": "123 Test St",
                "street2": "Suite 100",
            }
        )

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
