# Copyright (C) 2020 GARCO Consulting <www.garcoconsulting.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command

from odoo.addons.helpdesk_mgmt.tests import test_helpdesk_ticket


class CommonHelpdeskMgmtSla(test_helpdesk_ticket.TestHelpdeskTicket):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.calendar = cls.env["resource.calendar"].create(
            {
                "name": "24x7",
                "attendance_ids": [
                    Command.create(
                        {
                            "name": str(i),
                            "dayofweek": str(i),
                            "hour_from": 0,
                            "hour_to": 24,
                        }
                    )
                    for i in range(7)
                ],
            }
        )
        cls.stage1 = cls.env["helpdesk.ticket.stage"].create(
            {"name": "Stage One", "sequence": 1}
        )
        cls.stage2 = cls.env["helpdesk.ticket.stage"].create(
            {"name": "Stage Two", "sequence": 10}
        )
        cls.stage1_1 = cls.env["helpdesk.ticket.stage"].create(
            {"name": "Stage One-One", "sequence": 5}
        )
        cls.stage1_2 = cls.env["helpdesk.ticket.stage"].create(
            {"name": "Stage One-Two", "sequence": 6}
        )
        cls.stage3 = cls.env["helpdesk.ticket.stage"].create(
            {"name": "Stage Three", "sequence": 20}
        )
        cls.team1 = cls.env["helpdesk.ticket.team"].create(
            {
                "name": "Team SLA One",
                "resource_calendar_id": cls.calendar.id,
                "use_sla": True,
            }
        )
        cls.team2 = cls.env["helpdesk.ticket.team"].create(
            {
                "name": "Team SLA Two",
                "resource_calendar_id": cls.calendar.id,
                "use_sla": True,
            }
        )
        cls.stage1.team_ids = [Command.set([cls.team1.id, cls.team2.id])]
        cls.stage2.team_ids = [Command.set([cls.team1.id, cls.team2.id])]
        cls.category1 = cls.env["helpdesk.ticket.category"].create(
            {"name": "Category One"}
        )
        cls.category2 = cls.env["helpdesk.ticket.category"].create(
            {"name": "Category Two"}
        )
        cls.tag1 = cls.env["helpdesk.ticket.tag"].create({"name": "Tag One"})
        cls.tag2 = cls.env["helpdesk.ticket.tag"].create({"name": "Tag Two"})
        cls.env["helpdesk.sla"].search([("active", "=", True)]).write({"active": False})
        cls.sla = cls.env["helpdesk.sla"].create(
            {
                "name": "Generic SLA",
                "hours": 2,
                "stage_id": cls.stage2.id,
            }
        )
        cls.ticket1 = cls.get_ticket(cls.team1)
        cls.ticket2 = cls.get_ticket(cls.team2)
        cls.env["helpdesk.ticket"].search(
            [("id", "not in", (cls.ticket1 + cls.ticket2).ids)]
        ).active = False
        cls.user_sla = cls.env["res.users"].create(
            {
                "name": "SLA User",
                "login": "sla_user",
                "groups_id": [
                    Command.link(cls.env.ref("base.group_user").id),
                    Command.link(
                        cls.env.ref("helpdesk_mgmt.group_helpdesk_user_own").id
                    ),
                ],
            }
        )

    @classmethod
    def get_ticket(cls, team, extra_vals=None):
        vals = {
            "name": "Test Ticket",
            "description": "Ticket test",
            "team_id": team.id,
        }
        if extra_vals:
            vals.update(extra_vals)
        return cls.env["helpdesk.ticket"].create(vals)
