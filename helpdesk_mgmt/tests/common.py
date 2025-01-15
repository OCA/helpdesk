# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo.tests import new_test_user

from odoo.addons.base.tests.common import BaseCommon


class TestHelpdeskTicketBase(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        helpdesk_ticket_team = cls.env["helpdesk.ticket.team"]
        cls.company = cls.env.company
        cls.user_own = new_test_user(
            cls.env,
            login="helpdesk_mgmt-user_own",
            groups="helpdesk_mgmt.group_helpdesk_user_own",
        )
        cls.user_team = new_test_user(
            cls.env,
            login="helpdesk_mgmt-user_team",
            groups="helpdesk_mgmt.group_helpdesk_user_team",
        )
        cls.user = new_test_user(
            cls.env,
            login="helpdesk_mgmt-user",
            groups="helpdesk_mgmt.group_helpdesk_user",
        )
        cls.stage_closed = cls.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_done")
        cls.team_a = helpdesk_ticket_team.create(
            {"name": "Team A", "user_ids": [(6, 0, [cls.user_own.id, cls.user.id])]}
        )
        cls.team_b = helpdesk_ticket_team.create(
            {"name": "Team B", "user_ids": [(6, 0, [cls.user_team.id])]}
        )
        cls.new_stage = cls.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_new")
        cls.ticket_a_unassigned = cls._create_ticket(cls.team_a)
        cls.ticket_a_unassigned.priority = "3"
        cls.ticket_a_user_own = cls._create_ticket(cls.team_a, cls.user_own)
        cls.ticket_a_user_team = cls._create_ticket(cls.team_a, cls.user_team)
        cls.ticket_b_unassigned = cls._create_ticket(cls.team_b)
        cls.ticket_b_user_own = cls._create_ticket(cls.team_b, cls.user_own)
        cls.ticket_b_user_team = cls._create_ticket(cls.team_b, cls.user_team)

    @classmethod
    def _create_ticket(cls, team, user=False):
        ticket = cls.env["helpdesk.ticket"].create(
            {
                "name": "Ticket {} ({})".format(
                    team.name, user.login if user else "unassigned"
                ),
                "description": "Description",
                "team_id": team.id,
                "user_id": user.id if user else False,
                "priority": "1",
            }
        )
        # Since compute/depends method is added on user_id field
        # it's now necessary to write unassigned user for the tests
        if not user:
            ticket.user_id = False
        return ticket
