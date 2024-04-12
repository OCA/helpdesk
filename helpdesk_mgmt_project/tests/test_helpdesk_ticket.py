from odoo.addons.helpdesk_mgmt.tests.common import TestHelpdeskTicketBase


class TestHelpdeskTicketProject(TestHelpdeskTicketBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Ticket = cls.env["helpdesk.ticket"]
        Project = cls.env["project.project"]
        Task = cls.env["project.task"]
        Company = cls.env["res.company"]
        cls.company = Company.create({"name": "Test Last Company"})
        cls.ticket = cls.ticket_a_unassigned
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

    def test_helpdesk_ticket_default_company(self):
        self.env.user.groups_id += self.env.ref("project.group_project_manager")
        new_project = self.env["project.project"].create(
            {
                "name": "Test Helpdesk-Project Different Company",
                "company_id": self.company.id,
            }
        )
        ctx = {"default_project_id": new_project.id}
        ticket3 = (
            self.env["helpdesk.ticket"]
            .with_context(**ctx)
            .create(
                {
                    "name": "Test 3",
                    "description": "Ticket test3",
                }
            )
        )

        self.assertEqual(
            ticket3.project_id.name,
            "Test Helpdesk-Project Different Company",
            "Helpdesk Ticket: Ticket takes the project value defined in the context.",
        )

        self.assertTrue(
            self.ticket.company_id == self.ticket2.company_id == self.env.company,
            "Helpdesk Ticket: Tickets not created from a project take 'YourCompany' "
            "as the default company by default.",
        )

        self.assertFalse(
            ticket3.company_id.name == "YourCompany",
            "Helpdesk Ticket: Ticket created from a project does not take the company "
            "value set as default.",
        )

        self.assertEqual(
            ticket3.company_id,
            new_project.company_id,
            "Helpdesk Ticket: Ticket defaults to the company of the project.",
        )
