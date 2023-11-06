# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


from odoo.tests import common
from odoo.tests.common import new_test_user, users


class TestHelpdeskMgmtMaintenance(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = new_test_user(
            cls.env,
            login="helpdesk-user",
            groups="helpdesk_mgmt.group_helpdesk_user",
        )
        cls.equipment1 = cls.env["maintenance.equipment"].create(
            {
                "name": "Test equipment 1",
                "owner_user_id": cls.user.id,
                "allow_ticket": True,
            }
        )
        cls.equipment2 = cls.env["maintenance.equipment"].create(
            {
                "name": "Test equipment 2",
                "owner_user_id": cls.user.id,
                "allow_ticket": True,
            }
        )
        cls.ticket1 = cls.env["helpdesk.ticket"].create(
            {
                "name": "Test ticket 1",
                "description": "Test description 1",
            }
        )
        cls.ticket2 = cls.env["helpdesk.ticket"].create(
            {
                "name": "Test ticket 2",
                "description": "Test description 2",
                "equipment_ids": [(4, cls.equipment1.id), (4, cls.equipment2.id)],
            }
        )

    @users("helpdesk-user")
    def test_tickets(self):
        self.assertFalse(self.ticket1.has_equipments)
        self.assertTrue(self.ticket2.has_equipments)

        self.ticket1.equipment_ids = [(4, self.equipment1.id)]
        self.assertTrue(self.ticket1.has_equipments)

    @users("helpdesk-user")
    def test_equipments(self):
        self.assertEqual(self.equipment1.ticket_count, 1)
        self.assertEqual(self.equipment2.ticket_count, 1)

        self.ticket1.write({"equipment_ids": [(4, self.equipment1.id)]})
        self.equipment1.invalidate_cache()
        self.assertEqual(self.equipment1.ticket_count, 2)

        action = self.equipment2.action_view_tickets_equipment()
        self.assertEqual(
            action["context"]["default_equipment_ids"],
            [(4, self.equipment2.id)],
        )
