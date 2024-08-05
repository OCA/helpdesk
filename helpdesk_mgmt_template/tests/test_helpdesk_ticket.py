# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import tagged

from odoo.addons.helpdesk_mgmt.tests.common import TestHelpdeskTicketBase


@tagged("post_install", "-at_install")
class TestHelpdeskTicket(TestHelpdeskTicketBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        helpdesk_ticket_category_obj = cls.env["helpdesk.ticket.category"]
        cls.category_1 = helpdesk_ticket_category_obj.create(
            {"name": "Category 1", "template_description": "<h1>Description 1</h1>"}
        )
        cls.category_2 = helpdesk_ticket_category_obj.create(
            {"name": "Category 2", "template_description": "<h2>Description 2</h2>"}
        )
        cls.category_3 = helpdesk_ticket_category_obj.create(
            {"name": "Category 3", "template_description": "<h3>Description 3</h3>"}
        )
        helpdesk_ticket_team = cls.env["helpdesk.ticket.team"]

        cls.team_c = helpdesk_ticket_team.create(
            {
                "name": "Team C",
                "user_ids": [(6, 0, [cls.user_team.id])],
                "category_ids": [(6, 0, [cls.category_1.id, cls.category_3.id])],
            }
        )

    def test_set_category(self):
        """
        Test that setting a category on a ticket correctly sets the category_id and description.
        """
        # Check that the category_id is initially empty
        self.assertFalse(
            self.ticket_a_user_own.category_id,
            msg="Initially, the category_id should be empty",
        )

        # Set the category_id to the id of category_1
        self.ticket_a_user_own.category_id = self.category_1.id

        # Check that the category_id has been correctly set
        self.assertEqual(
            self.ticket_a_user_own.category_id.id,
            self.category_1.id,
            msg=f"The category ID #{self.category_1.id} was not correctly set",
        )

        # Check that the description has been correctly
        # set to the template_description of category_1
        self.assertEqual(
            self.ticket_a_user_own.description,
            self.category_1.template_description,
            msg=(
                "The description was not correctly set"
                " to the template_description of Category 1"
            ),
        )
        self.ticket_a_user_own.category_id = False
        self.assertEqual(
            self.ticket_a_user_own.description,
            self.category_1.template_description,
            msg=(
                "The description was not correctly set"
                " to the template_description of Category 1"
            ),
        )

    def test_check_available_team_categories(self):
        """
        Test the availability of team categories and
        their correct linking to the team and ticket.
        """
        # Check that initially, a team should not have categories attached to it.
        self.assertFalse(
            self.ticket_a_user_own.helpdesk_ticket_category_ids,
            msg="A team should not have categories attached to it.",
        )

        # Assign a team to the ticket and check that the categories are linked to the team.
        self.ticket_a_user_own.team_id = self.team_c.id
        related_category_ids = [self.category_1.id, self.category_3.id]
        self.assertEqual(
            self.ticket_a_user_own.helpdesk_ticket_category_ids.ids,
            related_category_ids,
            msg="Categories should be linked to the team.",
        )

        # Set the category_id of the ticket to the first category in the linked categories.
        self.ticket_a_user_own.category_id = (
            self.ticket_a_user_own.helpdesk_ticket_category_ids[0]
        )

        # Check that the category_id has been correctly set.
        self.assertEqual(
            self.ticket_a_user_own.category_id.id,
            self.category_1.id,
            msg=f"The category ID #{self.category_1.id} was not correctly set",
        )

    def test_create_ticket_with_category(self):
        """
        Test the creation of a ticket with a specific category and
        verify that the category is correctly set.
        """
        # Create a ticket with a specific category
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": f"Ticket {self.team_c.name} (test)",
                "team_id": self.team_c.id,
                "user_id": False,
                "description": "Test",
                "category_id": self.category_1.id,
                "priority": "1",
            }
        )

        # Check that the category_id has been correctly set
        self.assertEqual(
            ticket.category_id.id,
            self.category_1.id,
            msg=f"The category ID #{self.category_1.id} was not correctly set",
        )
