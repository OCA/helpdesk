# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo.tests import common, new_test_user


class TestHelpdeskTicketBase(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        helpdesk_ticket_team = cls.env["helpdesk.ticket.team"]
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        cls.user_own = new_test_user(
            cls.env,
            login="helpdesk_mgmt-user_own",
            groups="helpdesk_mgmt.group_helpdesk_user_own",
            context=ctx,
        )
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
        cls.stage_closed = cls.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_done")
        cls.team_a = helpdesk_ticket_team.create(
            {"name": "Team A", "user_ids": [(6, 0, [cls.user_own.id, cls.user.id])]}
        )
        cls.team_b = helpdesk_ticket_team.create(
            {"name": "Team B", "user_ids": [(6, 0, [cls.user_team.id])]}
        )
        cls.ticket_a_unassigned = cls._create_ticket(cls, cls.team_a)
        cls.ticket_a_unassigned.priority = "3"
        cls.ticket_a_user_own = cls._create_ticket(cls, cls.team_a, cls.user_own)
        cls.ticket_a_user_team = cls._create_ticket(cls, cls.team_a, cls.user_team)
        cls.ticket_b_unassigned = cls._create_ticket(cls, cls.team_b)
        cls.ticket_b_user_own = cls._create_ticket(cls, cls.team_b, cls.user_own)
        cls.ticket_b_user_team = cls._create_ticket(cls, cls.team_b, cls.user_team)

    def _create_ticket(self, team, user=False):
        return self.env["helpdesk.ticket"].create(
            {
                "name": "Ticket %s (%s)"
                % (team.name, user.login if user else "unassigned"),
                "description": "Description",
                "team_id": team.id,
                "user_id": user.id if user else False,
                "priority": "1",
            }
        )
