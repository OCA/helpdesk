import time

from odoo.tests import common, new_test_user


class TestHelpdeskTicket(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestHelpdeskTicket, cls).setUpClass()
        helpdesk_ticket = cls.env["helpdesk.ticket"]
        cls.Team = cls.env["helpdesk.ticket.team"]
        cls.user_admin = cls.env.ref("base.user_root")
        cls.user_demo = cls.env.ref("base.user_demo")
        cls.stage_closed = cls.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_done")

        cls.ticket = helpdesk_ticket.create(
            {"name": "Test 1", "description": "Ticket test"}
        )

    def test_helpdesk_ticket_datetimes(self):
        old_stage_update = self.ticket.last_stage_update

        self.assertTrue(
            self.ticket.last_stage_update,
            "Helpdesk Ticket: Helpdesk ticket should "
            "have a last_stage_update at all times.",
        )

        self.assertFalse(
            self.ticket.closed_date,
            "Helpdesk Ticket: No closed date "
            "should be set for a non closed "
            "ticket.",
        )

        time.sleep(1)

        self.ticket.write({"stage_id": self.stage_closed.id})

        self.assertTrue(
            self.ticket.closed_date,
            "Helpdesk Ticket: A closed ticket " "should have a closed_date value.",
        )
        self.assertTrue(
            old_stage_update < self.ticket.last_stage_update,
            "Helpdesk Ticket: The last_stage_update "
            "should be updated at every stage_id "
            "change.",
        )

        self.ticket.write({"user_id": self.user_admin.id})
        self.assertTrue(
            self.ticket.assigned_date,
            "Helpdesk Ticket: An assigned ticket " "should contain a assigned_date.",
        )

    def test_helpdesk_ticket_number(self):
        self.assertNotEqual(
            self.ticket.number,
            "/",
            "Helpdesk Ticket: A ticket should have " "a number.",
        )
        ticket_number_1 = int(self.ticket._prepare_ticket_number(values={})[2:])
        ticket_number_2 = int(self.ticket._prepare_ticket_number(values={})[2:])
        self.assertEqual(ticket_number_1 + 1, ticket_number_2)

    def test_helpdesk_ticket_copy(self):
        old_ticket_number = self.ticket.number

        copy_ticket_number = self.ticket.copy().number

        self.assertTrue(
            copy_ticket_number != "/" and old_ticket_number != copy_ticket_number,
            "Helpdesk Ticket: A new ticket can not "
            "have the same number than the origin ticket.",
        )

    def test_helpdesk_ticket_onchange_team(self):
        # When the team changes:
        #    if user_id is in team: do nothing
        #    if user_id is not in team: remove user_id
        #    if team exists: domain of user_id is users that are part of the team
        #    if team is false: domain of user_id is []

        ba_baracus = new_test_user(
            self.env, login="ba", groups="helpdesk_mgmt.group_helpdesk_manager"
        )
        hannibal_smith = new_test_user(
            self.env, login="hannibal", groups="helpdesk_mgmt.group_helpdesk_manager"
        )
        a_team = self.Team.create(
            {
                "name": "The A-Team",
                "user_ids": [(6, 0, [ba_baracus.id, hannibal_smith.id])],
            }
        )
        colonel_decker = new_test_user(
            self.env, login="decker", groups="helpdesk_mgmt.group_helpdesk_manager"
        )
        mp = self.Team.create(
            {
                "name": "Military Police",
                "user_ids": [(6, 0, [colonel_decker.id])],
            }
        )
        self.assertEqual(
            self.ticket._get_user_domain(),
            "[]",
            "User domain should be empty initially",
        )
        self.assertFalse(self.ticket.user_id, "User should be false initially")

        self.ticket.user_id = ba_baracus
        self.ticket.team_id = a_team

        self.assertEqual(self.ticket.team_id, a_team, "The team should be changed")
        self.assertEqual(
            self.ticket._get_user_domain(),
            "[('id', 'in', self.user_ids)]",
            "Only those users who are in team should be part of the domain",
        )
        self.assertItemsEqual(
            self.ticket.user_ids,
            a_team.user_ids,
            "The users list in ticket should be the same as in team",
        )
        self.assertEqual(
            self.ticket.user_id,
            ba_baracus,
            "If the current user is in the team, the user shouldn't be removed",
        )

        self.ticket.team_id = mp
        # Trigger @onchange manually since it only works with the form view
        self.ticket._onchange_dominion_user_id()

        self.assertFalse(
            self.ticket.user_id,
            "User should be removed if the user is not in the new team",
        )

        self.ticket.team_id = False

        self.assertEqual(
            self.ticket._get_user_domain(),
            "[]",
            "User domain should be empty if team is not set",
        )
