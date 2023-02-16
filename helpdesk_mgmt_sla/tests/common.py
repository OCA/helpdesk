# Copyright (C) 2020 GARCO Consulting <www.garcoconsulting.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields

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
        cls.ticket3 = cls.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket 3",
                "description": "Ticket test",
                "team_id": cls.team1.id,
                "assigned_date": fields.Datetime.now(),
            }
        )
        cls.ticket4 = cls.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket 4",
                "description": "Ticket test",
                "team_id": cls.team2.id,
                "assigned_date": fields.Datetime.now(),
                "closed_date": fields.Datetime.now() + timedelta(days=1),
            }
        )
        cls.sla = cls.env["helpdesk.sla"].create(
            {
                "name": "Test SLA 1",
                "hours": 2,
            }
        )
        cls.sla2 = cls.env["helpdesk.sla"].create(
            {
                "name": "Test SLA 2",
                "hours": 2,
                "sla_computation_id": cls.env.ref(
                    "helpdesk_mgmt.field_helpdesk_ticket__assigned_date"
                ).id,
                "sla_expiration_date": "fixed_date_field",
                "sla_expiration_id": cls.env.ref(
                    "helpdesk_mgmt.field_helpdesk_ticket__closed_date"
                ).id,
            }
        )
        cls.env["helpdesk.ticket"].search(
            [
                (
                    "id",
                    "not in",
                    (cls.ticket1 + cls.ticket2 + cls.ticket3 + cls.ticket4).ids,
                )
            ]
        ).active = False
