# Copyright (C) 2023 Binhex - Adasat Torres
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import new_test_user

from odoo.addons.base.tests.common import BaseCommon


class TestHelpdeskMotive(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Initialize the class object
        helpdesk_ticket_team = cls.env["helpdesk.ticket.team"]
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        cls.user_team = new_test_user(
            cls.env,
            login="helpdesk_mgmt-user_team",
            groups="helpdesk_mgmt.group_helpdesk_user_team",
            context=ctx,
        )
        cls.user = new_test_user(
            cls.env,
            login="helpdesk_mgmt-user",
            groups="helpdesk_mgmt.group_helpdesk_user",
            context=ctx,
        )
        cls.team_a = helpdesk_ticket_team.create(
            {"name": "Team A", "user_ids": [(6, 0, [cls.user.id])]}
        )
        cls.team_b = helpdesk_ticket_team.create(
            {"name": "Team B", "user_ids": [(6, 0, [cls.user_team.id])]}
        )

        cls.motive_id = cls.env["helpdesk.ticket.motive"].create(
            {"name": "motive_test", "team_id": cls.team_a.id}
        )

        cls.ticket_a_user_team = cls._create_ticket(
            cls, cls.team_a, cls.motive_id, cls.user_team
        )

    def _create_ticket(self, team, motive, user=False):
        return self.env["helpdesk.ticket"].create(
            {
                "name": "Ticket {} ({})".format(
                    team.name, user.login if user else "unassigned"
                ),
                "description": "Description",
                "team_id": team.id,
                "user_id": user.id if user else False,
                "priority": "1",
                "motive_id": motive.id,
            }
        )

    def test_compute_team_user_helpdesk_motive(self):
        self.assertTrue(self.ticket_a_user_team.motive_id)
        self.ticket_a_user_team.write({"team_id": self.team_b.id})
        self.assertFalse(self.ticket_a_user_team.motive_id)
        self.ticket_a_user_team.write({"motive_id": self.motive_id.id})
        self.assertTrue(self.ticket_a_user_team.motive_id)
        self.ticket_a_user_team.write({"user_id": self.user.id})
        self.assertFalse(self.ticket_a_user_team.motive_id)
