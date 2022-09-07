# Copyright (C) 2020 GARCO Consulting <www.garcoconsulting.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.helpdesk_mgmt.tests import test_helpdesk_ticket


class CommonHelpdeskMgmtSla(test_helpdesk_ticket.TestHelpdeskTicket):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.calendar = cls.env.ref("resource.resource_calendar_std")
        cls.stage1 = cls.env["helpdesk.ticket.stage"].create({"name": "Stage One"})
        cls.stage2 = cls.env["helpdesk.ticket.stage"].create({"name": "Stage Two"})
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
        cls.category1 = cls.env["helpdesk.ticket.category"].create(
            {"name": "Category One"}
        )
        cls.category2 = cls.env["helpdesk.ticket.category"].create(
            {"name": "Category Two"}
        )
        cls.tag1 = cls.env["helpdesk.ticket.tag"].create({"name": "Tag One"})
        cls.tag2 = cls.env["helpdesk.ticket.tag"].create({"name": "Tag Two"})
        cls.sla = cls.env["helpdesk.sla"].create(
            {
                "name": "Generic SLA",
                "hours": 2,
            }
        )
        cls.ticket1 = cls.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket 1",
                "description": "Ticket test",
                "team_id": cls.team1.id,
            }
        )
        cls.ticket2 = cls.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket 2",
                "description": "Ticket test",
                "team_id": cls.team2.id,
            }
        )
        cls.env["helpdesk.ticket"].search(
            [("id", "not in", (cls.ticket1 + cls.ticket2).ids)]
        ).active = False
