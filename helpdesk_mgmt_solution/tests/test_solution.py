# Copyright 2021 Sirum GmbH
# Copyright 2021 elego Software Solutions GmbH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class TestDefaults(TransactionCase):
    def setUp(self):
        super(TestDefaults, self).setUp()

        self.tag_1 = self.env.ref("helpdesk_mgmt.helpdesk_tag_1")
        self.tag_2 = self.env.ref("helpdesk_mgmt.helpdesk_tag_2")
        self.ticket_1 = self.env.ref("helpdesk_mgmt.helpdesk_ticket_1")
        self.ticket_2 = self.env.ref("helpdesk_mgmt.helpdesk_ticket_2")
        self.ticket_solution_1 = self.env.ref(
            "helpdesk_mgmt_solution.helpdesk_solution_1"
        )
        self.ticket_solution_2 = self.env.ref(
            "helpdesk_mgmt_solution.helpdesk_solution_2"
        )

    def test_button_create_solution(self):
        """
        Checks the creation of solution
        """
        self.assertEqual(self.ticket_1.solution_count, 1)
        self.assertEqual(self.ticket_1.solution_ids, self.ticket_solution_1)

    def test_add_solution_to_ticket(self):
        """ Add new solution to helpdesk ticket"""
        self.assertEqual(self.ticket_1.solution_count, 1)
        add_solution_wiz = (
            self.env["helpdesk.solution.wizard"]
            .with_context(
                add_solution=True,
                default_ticket_id=self.ticket_1.id,
            )
            .create({"solution_ids": [(4, self.ticket_solution_2.id)]})
        )
        add_solution_wiz.add_solution_to_ticket()
        self.assertEqual(self.ticket_1.solution_count, 2)

    def test_remove_solution_from_ticket(self):
        """ Remove solution from a helpdesk ticket"""
        self.assertEqual(self.ticket_2.solution_count, 1)
        self.ticket_2.solution_ids = [(4, self.ticket_solution_1.id)]
        self.assertEqual(self.ticket_2.solution_count, 2)

        remove_solution_wiz = (
            self.env["helpdesk.solution.wizard"]
            .with_context(
                remove_solution=True,
                default_ticket_id=self.ticket_2.id,
            )
            .create({"solution_ids": [(4, self.ticket_solution_2.id)]})
        )
        remove_solution_wiz.remove_solution_from_ticket()
        self.assertEqual(self.ticket_2.solution_count, 1)

    def test_search_solution_by_tags(self):
        """ Check search solution by tags"""
        search_solution_wiz = (
            self.env["helpdesk.solution.wizard"]
            .with_context(
                search_solution=True, search_default_tag_ids=[
                    (6, 0, self.tag_1.ids)
                ]
            )
            .create(
                {
                    "ticket_id": self.ticket_1.id,
                    "tag_ids": [(6, 0, self.tag_1.ids)],
                }
            )
        )
        res_action = search_solution_wiz.search_solution()
        search_ticket_id = res_action["context"]["helpdesk_ticket_id"]
        search_tags = res_action["context"]["search_default_tag_ids"]
        self.assertEqual(search_ticket_id, self.ticket_1.id)
        self.assertEqual(search_tags, self.tag_1.ids)

    def test_search_solution_by_title(self):
        """ Check search solution by title"""
        search_by_title_wiz = (
            self.env["helpdesk.solution.wizard"]
            .with_context(search_solution=True)
            .create(
                {
                    "ticket_id": self.ticket_1.id,
                    "title": self.ticket_solution_1.title,
                }
            )
        )
        res_action = search_by_title_wiz.search_solution()
        self.assertEqual(
            res_action["context"]["search_default_title"],
            self.ticket_solution_1.title
        )

    def test_search_solution_by_description(self):
        """ Check search solution by description"""
        search_by_title_wiz = (
            self.env["helpdesk.solution.wizard"]
            .with_context(search_solution=True)
            .create(
                {
                    "ticket_id": self.ticket_2.id,
                    "description": self.ticket_solution_2.description,
                }
            )
        )
        res_action = search_by_title_wiz.search_solution()
        search_ticket_id = res_action["context"]["helpdesk_ticket_id"]
        search_description = res_action["context"][
            "search_default_description"
        ]
        self.assertEqual(search_ticket_id, self.ticket_solution_2.id)
        self.assertEqual(
            search_description,
            self.ticket_solution_2.description
        )
