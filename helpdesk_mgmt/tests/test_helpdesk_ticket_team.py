from odoo.tests import common


class TestHelpdeskTicketTeam(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestHelpdeskTicketTeam, cls).setUpClass()
        helpdesk_ticket = cls.env["helpdesk.ticket"]
        helpdesk_ticket_team = cls.env["helpdesk.ticket.team"]
        mail_alias = cls.env["mail.alias"]
        cls.user_demo = cls.env.ref("base.user_demo")
        cls.stage_closed = cls.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_done")
        cls.mail_alias_id = mail_alias.create(
            {
                "alias_name": "Test Mail Alias",
                "alias_model_id": cls.env["ir.model"]
                .search([("model", "=", "helpdesk.ticket")])
                .id,
            }
        )
        cls.team_id = helpdesk_ticket_team.create(
            {"name": "Team 1", "alias_id": cls.mail_alias_id.id}
        )
        cls.helpdesk_ticket_1 = helpdesk_ticket.create(
            {
                "name": "Ticket 1",
                "description": "Description",
                "team_id": cls.team_id.id,
                "priority": "3",
            }
        )
        cls.helpdesk_ticket_2 = helpdesk_ticket.create(
            {
                "name": "Ticket 2",
                "description": "Description",
                "team_id": cls.team_id.id,
                "user_id": cls.user_demo.id,
                "priority": "1",
            }
        )

    def test_helpdesk_ticket_todo(self):
        self.assertEqual(
            self.team_id.todo_ticket_count,
            2,
            "Helpdesk Ticket: Helpdesk ticket team should " "have two tickets to do.",
        )
        self.assertEqual(
            self.team_id.todo_ticket_count_unassigned,
            1,
            "Helpdesk Ticket: Helpdesk ticket team should "
            "have one tickets unassigned.",
        )
        self.assertEqual(
            self.team_id.todo_ticket_count_high_priority,
            1,
            "Helpdesk Ticket: Helpdesk ticket team should "
            "have two tickets with high priority.",
        )
        self.assertEqual(
            self.team_id.todo_ticket_count_unattended,
            2,
            "Helpdesk Ticket: Helpdesk ticket team should "
            "have two tickets unattended.",
        )

        self.helpdesk_ticket_1.write({"stage_id": self.stage_closed.id})

        self.assertEqual(
            self.team_id.todo_ticket_count_unattended,
            1,
            "Helpdesk Ticket: Helpdesk ticket team should "
            "have one ticket unattended.",
        )

        self.assertEqual(
            self.team_id.todo_ticket_count,
            1,
            "Helpdesk Ticket: Helpdesk ticket team should " "have one ticket to do.",
        )
