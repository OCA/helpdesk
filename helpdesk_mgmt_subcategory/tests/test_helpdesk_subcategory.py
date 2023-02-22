from odoo.addons.helpdesk_mgmt.tests import test_helpdesk_ticket


class TestHelpdeskTicketSubcategory(test_helpdesk_ticket.TestHelpdeskTicket):
    @classmethod
    def setUpClass(cls):
        super(TestHelpdeskTicketSubcategory, cls).setUpClass()
        env = cls.env(user=cls.user_admin)
        Ticket = env["helpdesk.ticket"]
        Category = env["helpdesk.ticket.category"]
        Tag = env["helpdesk.ticket.tag"]

        cls.tag1 = Tag.create({"name": "tk1"})
        cls.ticket2 = Ticket.create({"name": "Test 2", "description": "Ticket test2"})
        cls.root_category = Category.create({"name": "Root"})
        cls.category1 = Category.create(
            {"name": "Cat1", "parent_id": cls.root_category.id}
        )
        cls.category2 = Category.create(
            {"name": "Cat2", "parent_id": cls.root_category.id}
        )
        cls.ticket.write(
            {"category_id": cls.category1.id, "tag_ids": [(6, 0, [cls.tag1.id])]}
        )
        cls.ticket2.write(
            {"category_id": cls.category2.id, "tag_ids": [(6, 0, [cls.tag1.id])]}
        )

    def test_helpdesk_category(self):
        self.assertEqual(
            self.category1.code, "root-cat1", "Helpdesk Category: Wrong category code"
        )
        self.assertEqual(self.category1.complete_name, "Root / Cat1")

    def test_helpdesk_tickets_by_category(self):
        self.assertEqual(
            len(self.root_category.child_ids),
            2,
            "Helpdesk Category: Should have two children categories",
        )
        self.assertEqual(
            self.category1.tickets_count,
            1,
            "Helpdesk Category1: Should have one ticket",
        )
        self.assertEqual(
            self.root_category.tickets_count,
            2,
            "Helpdesk root category should have 2 tickets",
        )

    def test_helpdesk_tickets_by_tag(self):
        self.assertEqual(self.tag1.tickets_count, 2, "Tag 1 should have 2 tickets")
