# Copyright (C) 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestPortalTicketEquipment(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Ticket Customer"})
        cls.other_partner = cls.env["res.partner"].create({"name": "Someone Else"})
        cls.portal_user = (
            cls.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "login": "portal-ticket@test.example.com",
                    "name": "Portal Ticket User",
                    "partner_id": cls.partner.id,
                    "groups_id": [(6, 0, [cls.env.ref("base.group_portal").id])],
                    "password": "portal-ticket",
                }
            )
        )
        cls.location = cls.env["fsm.location"].create(
            {"name": "Customer Site", "owner_id": cls.partner.id}
        )
        cls.equipment = cls.env["fsm.equipment"].create(
            {
                "name": "Customer Device",
                "owned_by_id": cls.partner.id,
                "location_id": cls.location.id,
            }
        )
        cls.foreign_equipment = cls.env["fsm.equipment"].create(
            {"name": "Foreign Device", "owned_by_id": cls.other_partner.id}
        )
        cls.team = cls.env["helpdesk.ticket.team"].create({"name": "Support"})

    def _auth(self):
        self.authenticate("portal-ticket@test.example.com", "portal-ticket")

    def _csrf(self):
        return (
            self.opener.get(self.base_url() + "/new/ticket")
            .text.split('name="csrf_token"')[1]
            .split('value="')[1]
            .split('"')[0]
        )

    def _submit(self, equipment_id):
        return self.url_open(
            "/submitted/ticket",
            data={
                "subject": "Broken device",
                "description": "It broke",
                "equipment": str(equipment_id),
                "category": "",
                "csrf_token": self._csrf(),
            },
        )

    def test_new_ticket_page_lists_own_equipments(self):
        self._auth()
        response = self.url_open("/new/ticket")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Customer Device", response.content)
        self.assertNotIn(b"Foreign Device", response.content)

    def test_submit_with_own_equipment_sets_location(self):
        self._auth()
        self._submit(self.equipment.id)
        ticket = self.env["helpdesk.ticket"].search([("name", "=", "Broken device")])
        self.assertTrue(ticket)
        self.assertEqual(ticket.equipment_id, self.equipment)
        self.assertEqual(ticket.fsm_location_id, self.location)

    def test_submit_with_foreign_equipment_is_ignored(self):
        self._auth()
        self._submit(self.foreign_equipment.id)
        ticket = self.env["helpdesk.ticket"].search([("name", "=", "Broken device")])
        self.assertTrue(ticket)
        self.assertFalse(ticket.equipment_id)

    def test_submit_with_garbage_equipment_is_ignored(self):
        self._auth()
        self._submit("not-a-number")
        ticket = self.env["helpdesk.ticket"].search([("name", "=", "Broken device")])
        self.assertTrue(ticket)
        self.assertFalse(ticket.equipment_id)
