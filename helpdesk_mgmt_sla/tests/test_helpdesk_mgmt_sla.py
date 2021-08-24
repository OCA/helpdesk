# Copyright (C) 2020 GARCO Consulting <www.garcoconsulting.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo.addons.helpdesk_mgmt.tests import test_helpdesk_ticket

_log = logging.getLogger(__name__)


class TestHelpdeskMgmtSla(test_helpdesk_ticket.TestHelpdeskTicket):
    @classmethod
    def setUpClass(cls):
        super(TestHelpdeskMgmtSla, cls).setUpClass()
        cls.team_id = cls.env["helpdesk.ticket.team"].create(
            {"name": "Team SLA", "use_sla": True}
        )
        cls.stage_id = cls.env["helpdesk.ticket.stage"].create({"name": "Reach stage"})
        cls.sla_id = cls.env["helpdesk.sla"].create(
            {
                "name": "Generic SLA",
                "team_ids": [(6, 0, [cls.team_id.id])],
                "stage_id": cls.stage_id.id,
                "hours": 2,
            }
        )
        cls.ticket = cls.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket 1",
                "description": "Ticket test",
                "team_id": cls.team_id.id,
            }
        )

    def test_helpdesk_mgmt_sla(self):
        self.ticket._compute_team_sla()
        self.assertEqual(self.ticket.sla_expired, False)

    def test_helpdesk_sla(self):
        self.env["helpdesk.sla"].check_sla()
        self.assertEqual(self.ticket.sla_expired, False)
