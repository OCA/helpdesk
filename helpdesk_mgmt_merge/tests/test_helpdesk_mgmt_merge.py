from odoo.addons.base.tests.common import BaseCommon


class TestHelpdeskTicketMerge(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.HelpdeskTicketMerge = cls.env["helpdesk.ticket.merge"]
        cls.ticket_1 = cls._create_ticket(cls, "Ticket 1", "Description for Ticket 1")
        cls.ticket_2 = cls._create_ticket(cls, "Ticket 2", "Description for Ticket 2")

    def _create_ticket(self, name, description):
        return self.env["helpdesk.ticket"].create(
            {
                "name": name,
                "description": description,
            }
        )

    def test_helpdesk_ticket_merge_create_new_ticket(self):
        self.ticket_merge_1 = self.HelpdeskTicketMerge.with_context(
            active_ids=[self.ticket_1.id, self.ticket_2.id]
        ).create({"create_new_ticket": True, "dst_ticket_name": "Test 1"})
        self.ticket_merge_1.merge_tickets()
        self.assertEqual(self.ticket_merge_1.dst_ticket_id.name, "Test 1")

    def test_helpdesk_ticket_merge_with_existing_ticket(self):
        self.ticket_merge_2 = self.HelpdeskTicketMerge.with_context(
            active_ids=[self.ticket_1.id, self.ticket_2.id]
        ).create({})
        self.assertFalse(self.ticket_merge_2.user_id)
        self.ticket_2.user_id = self.env.user.id
        self.ticket_merge_2.dst_ticket_id = self.ticket_2.id
        self.ticket_merge_2._onchange_dst_ticket_id()
        self.assertTrue(self.ticket_merge_2.user_id)
        self.ticket_merge_2.merge_tickets()
        self.assertEqual(self.ticket_merge_2.dst_ticket_id.name, "Ticket 2")
