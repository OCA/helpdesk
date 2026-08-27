# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo.tests import new_test_user

from odoo.addons.base.tests.common import BaseCommon


class TestResPartner(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ticket_obj = cls.env["helpdesk.ticket"]
        cls.stage_closed = cls.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_done")
        cls.user = new_test_user(cls.env, login="helpdesk_mgmt_partner_dashboard-user")

        cls.root = cls.env["res.partner"].create({"name": "Root Partner"})
        cls.child = cls.env["res.partner"].create(
            {"name": "Child Partner", "parent_id": cls.root.id}
        )
        cls.grandchild = cls.env["res.partner"].create(
            {"name": "Grandchild Partner", "parent_id": cls.child.id}
        )

        cls.ticket_root_unassigned = cls._create_ticket(cls.root, priority="3")
        cls.ticket_child_assigned = cls._create_ticket(cls.child, cls.user)
        cls.ticket_grandchild = cls._create_ticket(cls.grandchild)

    @classmethod
    def _create_ticket(cls, partner, user=False, priority="1"):
        return cls.ticket_obj.create(
            {
                "name": "Ticket {} ({})".format(
                    partner.name, user.login if user else "unassigned"
                ),
                "description": "Description",
                "partner_id": partner.id,
                "user_id": user.id if user else False,
                "priority": priority,
            }
        )

    def test_todo_ticket_count_rolls_up_the_whole_hierarchy(self):
        self.assertEqual(
            self.root.todo_ticket_count,
            3,
            "Helpdesk Ticket: Root should count its own ticket plus its "
            "child's and grandchild's.",
        )
        self.assertEqual(
            self.child.todo_ticket_count,
            2,
            "Helpdesk Ticket: Child should count its own ticket plus its "
            "child's (the grandchild), not the root's.",
        )
        self.assertEqual(
            self.grandchild.todo_ticket_count,
            1,
            "Helpdesk Ticket: Grandchild has no children, only its own ticket.",
        )

    def test_todo_ticket_count_unassigned(self):
        self.assertEqual(
            self.root.todo_ticket_count_unassigned,
            2,
            "Helpdesk Ticket: Root's unassigned count should include the "
            "grandchild's unassigned ticket too.",
        )

    def test_todo_ticket_count_high_priority(self):
        self.assertEqual(
            self.root.todo_ticket_count_high_priority,
            1,
            "Helpdesk Ticket: Only the root's own ticket is high priority.",
        )
        self.assertEqual(
            self.child.todo_ticket_count_high_priority,
            0,
            "Helpdesk Ticket: The high priority ticket belongs to the root, "
            "not to any of its descendants.",
        )

    def test_todo_ticket_count_unattended(self):
        self.assertEqual(self.root.todo_ticket_count_unattended, 3)

        self.ticket_grandchild.write({"stage_id": self.stage_closed.id})

        self.assertEqual(
            self.root.todo_ticket_count_unattended,
            2,
            "Helpdesk Ticket: Closing the grandchild's ticket should lower "
            "the root's rolled-up unattended count.",
        )
        self.assertEqual(
            self.root.todo_ticket_count,
            2,
            "Helpdesk Ticket: Closing the grandchild's ticket should lower "
            "the root's rolled-up todo count.",
        )

    def test_search_todo_ticket_count(self):
        no_tickets = self.env["res.partner"].create({"name": "No Tickets"})

        found = self.env["res.partner"].search([("todo_ticket_count", "=", True)])
        self.assertIn(self.root.id, found.ids)
        self.assertNotIn(no_tickets.id, found.ids)

        not_found = self.env["res.partner"].search([("todo_ticket_count", "=", False)])
        self.assertIn(no_tickets.id, not_found.ids)
        self.assertNotIn(self.root.id, not_found.ids)
