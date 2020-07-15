from odoo.tests import common


class TestHelpdeskTicketTeam(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestHelpdeskTicketTeam, cls).setUpClass()
        helpdesk_ticket = cls.env["helpdesk.ticket"]
        helpdesk_ticket_team = cls.env["helpdesk.ticket.team"]
        cls.user_demo = cls.env.ref("base.user_demo")
        cls.stage_closed = cls.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_done")
        cls.team_id = helpdesk_ticket_team.create({"name": "Team 1"})
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
                "priority": "3",
            }
        )

    def test_todo(self):
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
            2,
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

    def test_getters(self):
        team_endpoint = "team-1"

        self.team_id.enable_webform = True
        self.assertTrue(self.team_id.enable_webform)
        self.team_id._compute_endpoint_webform()
        self.assertEqual(self.team_id.endpoint_webform, team_endpoint)
        self.assertEqual(
            self.team_id.endpoint_full_webform, "help/team/{}".format(team_endpoint)
        )

        _team_id = self.env["helpdesk.ticket.team"].create({"name": "Team 1"})
        _team_id.enable_webform = True
        self.assertTrue(_team_id.enable_webform)
        _team_id._compute_endpoint_webform()
        self.assertEqual(
            _team_id.endpoint_webform, "{}-{}".format(team_endpoint, _team_id.id)
        )
        self.assertNotEqual(_team_id.endpoint_view_id.id, False)
        _team_id.endpoint_view_id.unlink()
        self.assertEqual(_team_id.endpoint_view_id.id, False)
        _team_id.compute_endpoint_view_id()
        self.assertNotEqual(_team_id.endpoint_view_id.id, False)
        self.assertEqual(
            _team_id.endpoint_view_id.xml_id,
            f"{self.env.ref('helpdesk_mgmt.portal_create_ticket_inner_form').xml_id}"
            f"_{_team_id.id}",
        )
        self.assertEqual(
            _team_id.endpoint_full_webform,
            "help/team/{}-{}".format(team_endpoint, _team_id.id),
        )
        _team_id.name = "team-69"
        _team_id.recompute_endpoint()
        self.assertEqual(
            _team_id.endpoint_full_webform, "help/team/{}".format("team-69"),
        )
