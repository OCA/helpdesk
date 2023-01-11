from odoo.addons.helpdesk_mgmt.tests import test_helpdesk_ticket


class TestHelpdeskType(test_helpdesk_ticket.TestHelpdeskTicket):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Ticket = cls.env["helpdesk.ticket"]
        Team = cls.env["helpdesk.ticket.team"]
        Type = cls.env["helpdesk.ticket.type"]

        cls.ht_team1 = Team.create({"name": "Team 1", "user_ids": [(4, cls.user.id)]})
        cls.ht_type1 = Type.create(
            {"name": "Type 1", "team_ids": [(4, cls.ht_team1.id)]}
        )
        cls.ht_type2 = Type.create({"name": "Type 2"})
        cls.ht_ticket1 = Ticket.create(
            {"name": "Test 1", "description": "Ticket test 1"}
        )

    def test_helpdesk_onchange_type_id(self):
        self.ht_ticket1.write({"team_id": self.ht_team1.id, "user_id": self.user.id})

        self.ht_ticket1.type_id = self.ht_type1
        self.ht_ticket1._onchange_type_id()
        self.assertEqual(
            self.ht_ticket1.team_id,
            self.ht_team1,
            "Helpdesk Ticket: when type is changed, ticket team should be unchanged"
            " if current team belongs to the new type",
        )
        self.assertEqual(
            self.ht_ticket1.user_id,
            self.user,
            "Helpdesk Ticket: when type is changed, ticket user should be unchanged"
            " if user belongs to a that belongs to the new type",
        )

        self.ht_ticket1.type_id = self.ht_type2
        self.ht_ticket1._onchange_type_id()
        self.assertFalse(
            self.ht_ticket1.team_id,
            "Helpdesk Ticket: When type is changed, ticket team should be reset if"
            " current team does not belong to the new type",
        )
        self.assertFalse(
            self.ht_ticket1.user_id,
            "Helpdesk Ticket: When type is changed, ticket user should be reset if"
            " current user does not belong to a team assigned to the new type",
        )
