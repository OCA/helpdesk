from odoo.tools.safe_eval import safe_eval

from odoo.addons.helpdesk_mgmt.tests.common import TestHelpdeskTicketBase


class TestHelpdeskTicketProject(TestHelpdeskTicketBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Ticket = cls.env["helpdesk.ticket"]
        Project = cls.env["project.project"]
        Task = cls.env["project.task"]
        cls.ticket = cls.ticket_a_unassigned
        cls.ticket2 = Ticket.create({"name": "Test 2", "description": "Ticket test2"})
        cls.project1 = Project.create({"name": "Test Helpdesk-Project 1"})
        cls.milestone = cls.env["project.milestone"].create(
            {"name": "My milestone", "project_id": cls.project1.id}
        )
        cls.task_project1 = Task.create(
            {"name": "Test Task Helpdesk-Project 1", "project_id": cls.project1.id}
        )
        cls.project2 = Project.create({"name": "Test Helpdesk-Project 2"})
        cls.task_project2 = Task.create(
            {"name": "Test Task Helpdesk-Project 2", "project_id": cls.project2.id}
        )
        cls.ticket.write(
            {"project_id": cls.project1.id, "task_id": cls.task_project1.id}
        )
        cls.ticket2.write(
            {"project_id": cls.project1.id, "task_id": cls.task_project1.id}
        )

    def test_helpdesk_ticket_project_task(self):
        self.ticket.write({"project_id": self.project2.id})
        self.assertFalse(
            self.ticket.task_id,
            "Helpdesk Ticket: When change the project "
            "the ticket task should be reset.",
        )

    def test_helpdesk_ticket_counts(self):
        self.assertEqual(
            self.project1.ticket_count,
            2,
            "Helpdesk Ticket: Project should have two related tickets.",
        )
        self.assertEqual(
            self.project1.todo_ticket_count,
            2,
            "Helpdesk Ticket: Project should have two related todo tickets.",
        )
        self.assertEqual(
            self.task_project1.ticket_count,
            2,
            "Helpdesk Ticket: Task have two realted tickets.",
        )
        self.assertEqual(
            self.task_project1.todo_ticket_count,
            2,
            "Helpdesk Ticket: Task have two realted tickets.",
        )
        self.assertEqual(
            self.project2.ticket_count,
            0,
            "Helpdesk Ticket: Project should have two related tickets.",
        )
        self.assertEqual(
            self.task_project2.ticket_count,
            0,
            "Helpdesk Ticket: Task have two realted tickets.",
        )
        self.ticket.write({"stage_id": self.stage_closed.id})
        self.assertEqual(
            self.project1.ticket_count,
            2,
            "Helpdesk Ticket: Project should have two related tickets.",
        )
        self.assertEqual(
            self.project1.todo_ticket_count,
            1,
            "Helpdesk Ticket: Project should have one related todo tickets.",
        )
        self.assertEqual(
            self.task_project1.todo_ticket_count,
            1,
            "Helpdesk Ticket: Task have one realted tickets.",
        )

    def test_compute_ticket_count(self):
        """Test computation of ticket_count and todo_ticket_count on tasks"""
        self.assertEqual(self.task_project1.ticket_count, 2)
        self.assertEqual(self.task_project1.todo_ticket_count, 2)

        # Close one ticket and check counts again
        self.ticket.write({"stage_id": self.stage_closed.id})
        self.assertEqual(self.task_project1.ticket_count, 2)
        self.assertEqual(self.task_project1.todo_ticket_count, 1)

    def test_action_view_ticket(self):
        """Test action_view_ticket for correct domain and view modes"""
        action = self.task_project1.action_view_ticket()
        self.assertEqual(
            action["domain"], f"[('id','in',{self.task_project1.ticket_ids.ids})]"
        )
        # If only one ticket, should open in form view
        single_ticket_task = self.env["project.task"].create(
            {"name": "Single Ticket Task", "project_id": self.project1.id}
        )
        self.ticket.write({"task_id": single_ticket_task.id})
        action = single_ticket_task.action_view_ticket()
        self.assertEqual(action["res_id"], self.ticket.id)

    def test_project_update_buttons(self):
        """Test that the project update button is only visible to users with the
        'Project / Project Manager' group.
        """
        user = self._create_new_internal_user(groups="project.group_project_user")

        buttons = self.project1.with_user(user)._get_stat_buttons()
        self.assertFalse(
            any(
                button["action"] == "action_open_helpdesk_tickets" for button in buttons
            )
        )
        buttons = self.project1._get_stat_buttons()
        self.assertTrue(
            any(
                button["action"] == "action_open_helpdesk_tickets" for button in buttons
            )
        )
        action = self.project1.action_open_helpdesk_tickets()
        tickets = self.env[action["res_model"]].search(action["domain"])
        self.assertEqual(len(tickets), 2)
        self.assertIn(self.ticket, tickets)
        self.assertIn(self.ticket2, tickets)

    def test_milestones(self):
        ticket_1 = self.env["helpdesk.ticket"].create(
            {
                "name": "Test ticket 01",
                "description": "Test Ticket",
                "project_id": self.project1.id,
            }
        )
        self.assertFalse(ticket_1.milestone_id)
        self.assertEqual(0, self.milestone.helpdesk_ticket_count)
        task = self.env["project.task"].create(
            {
                "name": "My test task",
                "project_id": self.project1.id,
                "milestone_id": self.milestone.id,
            }
        )
        ticket_1.task_id = task
        self.assertEqual(ticket_1.milestone_id, self.milestone)
        self.assertEqual(1, self.milestone.helpdesk_ticket_count)
        action = self.milestone.action_view_helpdesk_ticket()
        self.assertIn("res_id", action)
        self.assertEqual(action["res_id"], ticket_1.id)
        ticket_2 = self.env["helpdesk.ticket"].create(
            {
                "name": "Test ticket 02",
                "description": "Test Ticket",
                "project_id": self.project1.id,
                "milestone_id": self.milestone.id,
            }
        )
        self.milestone.invalidate_recordset()
        self.assertEqual(2, self.milestone.helpdesk_ticket_count)
        action = self.milestone.action_view_helpdesk_ticket()
        self.assertFalse(action.get("res_id"))
        milestone_requests = self.env[action["res_model"]].search(
            safe_eval(action["domain"], locals_dict={"active_id": self.milestone.id})
        )
        self.assertEqual(2, len(milestone_requests))
        self.assertIn(ticket_1, milestone_requests)
        self.assertIn(ticket_2, milestone_requests)
