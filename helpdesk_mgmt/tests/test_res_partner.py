from odoo.addons.base.tests.common import BaseCommon


class TestPartner(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_obj = cls.env["res.partner"]
        cls.ticket_obj = cls.env["helpdesk.ticket"]
        cls.stage_id_closed = cls.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_done")
        cls.parent_id = cls.partner_obj.create({"name": "Parent 1"})
        cls.child_id_1 = cls.partner_obj.create({"name": "Child 1"})
        cls.child_id_2 = cls.partner_obj.create({"name": "Child 2"})
        cls.child_id_3 = cls.partner_obj.create({"name": "Child 3"})
        cls.tickets = []
        cls.parent_id.child_ids = [
            (4, cls.child_id_1.id),
            (4, cls.child_id_2.id),
            (4, cls.child_id_3.id),
        ]
        for i in [69, 155, 314, 420]:
            cls.tickets.append(
                cls.ticket_obj.create(
                    {
                        "name": f"Nice ticket {i}",
                        "description": f"Nice ticket {i} description",
                    }
                )
            )
        cls.parent_id.helpdesk_ticket_ids = [(4, cls.tickets[0].id)]
        cls.child_id_1.helpdesk_ticket_ids = [(4, cls.tickets[1].id)]
        cls.child_id_2.helpdesk_ticket_ids = [(4, cls.tickets[2].id)]
        cls.child_id_3.helpdesk_ticket_ids = [(4, cls.tickets[3].id)]
        cls.child_id_3.helpdesk_ticket_ids[-1].stage_id = cls.stage_id_closed

    def test_ticket_count(self):
        self.assertEqual(self.parent_id.helpdesk_ticket_count, 4)

    def test_ticket_active_count(self):
        self.assertEqual(self.parent_id.helpdesk_ticket_active_count, 3)

    def test_ticket_string(self):
        self.assertEqual(self.parent_id.helpdesk_ticket_count_string, "3 / 4")
