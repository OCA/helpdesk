from odoo.addons.helpdesk_mgmt.tests import test_helpdesk_ticket


class TestHelpdeskTicketProject(test_helpdesk_ticket.TestHelpdeskTicket):
    @classmethod
    def setUpClass(cls):
        super(TestHelpdeskTicketProject, cls).setUpClass()
        env = cls.env(user=cls.user_admin)
        Ticket = env["helpdesk.ticket"]
        Project = env["project.project"]
        Task = env["project.task"]
        cls.ticket2 = Ticket.create({"name": "Test 2", "description": "Ticket test2"})
        cls.project1 = Project.create({"name": "Test Helpdesk-Project 1"})
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
            "Helpdesk Ticket: Project should " "have two related tickets.",
        )
        self.assertEqual(
            self.project1.todo_ticket_count,
            2,
            "Helpdesk Ticket: Project should " "have two related todo tickets.",
        )
        self.assertEqual(
            self.task_project1.ticket_count,
            2,
            "Helpdesk Ticket: Task " "have two realted tickets.",
        )
        self.assertEqual(
            self.task_project1.todo_ticket_count,
            2,
            "Helpdesk Ticket: Task " "have two realted tickets.",
        )
        self.assertEqual(
            self.project2.ticket_count,
            0,
            "Helpdesk Ticket: Project should " "have two related tickets.",
        )
        self.assertEqual(
            self.task_project2.ticket_count,
            0,
            "Helpdesk Ticket: Task " "have two realted tickets.",
        )
        self.ticket.write({"stage_id": self.stage_closed.id})
        self.assertEqual(
            self.project1.ticket_count,
            2,
            "Helpdesk Ticket: Project should " "have two related tickets.",
        )
        self.assertEqual(
            self.project1.todo_ticket_count,
            1,
            "Helpdesk Ticket: Project should " "have one related todo tickets.",
        )
        self.assertEqual(
            self.task_project1.todo_ticket_count,
            1,
            "Helpdesk Ticket: Task " "have one realted tickets.",
        )
