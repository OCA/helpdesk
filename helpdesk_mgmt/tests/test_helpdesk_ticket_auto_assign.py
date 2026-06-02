# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo.tests import new_test_user

from odoo.addons.base.tests.common import BaseCommon


class TestHelpdeskAutoAssign(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Ticket = cls.env["helpdesk.ticket"]
        cls.Team = cls.env["helpdesk.ticket.team"]
        # Isolate the team assignment method from the company-level
        # "assign to creator" default.
        cls.env.company.helpdesk_mgmt_ticket_auto_assign = False
        cls.user_a = new_test_user(cls.env, login="hd-assign-a")
        cls.user_b = new_test_user(cls.env, login="hd-assign-b")
        cls.tag_lang = cls.env["helpdesk.ticket.tag"].create({"name": "Spanish"})
        cls.tag_other = cls.env["helpdesk.ticket.tag"].create({"name": "Hardware"})
        cls.stage_closed = cls.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_done")

    def _new_team(self, method, members):
        return self.Team.create(
            {
                "name": f"Auto Team {method}",
                "assign_method": method,
                "user_ids": [(6, 0, members.ids)],
            }
        )

    def _new_ticket(self, team, **vals):
        values = {
            "name": "Auto ticket",
            "description": "x",
            "team_id": team.id,
        }
        values.update(vals)
        return self.Ticket.create(values)

    def test_manual_no_assignment(self):
        team = self._new_team("manual", self.user_a + self.user_b)
        ticket = self._new_ticket(team)
        self.assertFalse(ticket.user_id)

    def test_randomly_round_robin(self):
        members = self.user_a + self.user_b
        team = self._new_team("randomly", members)
        ordered = members.sorted("id")
        t1 = self._new_ticket(team)
        t2 = self._new_ticket(team)
        t3 = self._new_ticket(team)
        self.assertEqual(t1.user_id, ordered[0])
        self.assertEqual(t2.user_id, ordered[1])
        self.assertEqual(t3.user_id, ordered[0])

    def test_balanced_least_busy(self):
        team = self._new_team("balanced", self.user_a + self.user_b)
        # Seed an open ticket already assigned to user_a.
        self._new_ticket(team, user_id=self.user_a.id)
        # The next unassigned ticket must go to the idle member.
        ticket = self._new_ticket(team)
        self.assertEqual(ticket.user_id, self.user_b)

    def test_tags_within_pool(self):
        team = self._new_team("tags", self.user_a + self.user_b)
        self.env["helpdesk.ticket.team.assignment.tag"].create(
            {
                "team_id": team.id,
                "tag_id": self.tag_lang.id,
                "user_ids": [(6, 0, self.user_a.ids)],
            }
        )
        mapped = self._new_ticket(team, tag_ids=[(6, 0, self.tag_lang.ids)])
        self.assertEqual(mapped.user_id, self.user_a)
        # A tag without mapping leaves the ticket unassigned.
        unmapped = self._new_ticket(team, tag_ids=[(6, 0, self.tag_other.ids)])
        self.assertFalse(unmapped.user_id)

    def test_no_members(self):
        team = self._new_team("randomly", self.env["res.users"])
        ticket = self._new_ticket(team)
        self.assertFalse(ticket.user_id)

    def test_folded_stage_not_assigned(self):
        team = self._new_team("randomly", self.user_a + self.user_b)
        ticket = self._new_ticket(team, stage_id=self.stage_closed.id)
        self.assertFalse(ticket.user_id)
