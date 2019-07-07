# Copyright 2019 Georg Notter <georg.notter@agenterp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase
from odoo.exceptions import ValidationError


class TestHelpdeskTicket(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestHelpdeskTicket, cls).setUpClass()
        cls.user_demo = cls.env.ref("base.user_demo")
        cls.stage_done = cls.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_done")
        cls.project1 = cls.env["project.project"].create({"name": "Test Project 1"})
        cls.ticket = cls.env["helpdesk.ticket"].create(
            {
                "name": "Test Helpdesk Ticket",
                "description": "Test Helpdesk Description",
                "project_id": cls.project1.id,
            }
        )

    def test_helpdesk_ticket_datetimes(self):
        self.stage_done.timesheet_required = True
        with self.assertRaises(ValidationError):
            self.ticket.stage_id = self.stage_done
        timesheet_line = self.ticket.timesheet_ids.new()
        timesheet_line.user_id = self.user_demo.id
        timesheet_line.name = "Timesheet Line 1"
        timesheet_line.account_id = self.project1.analytic_account_id
        self.ticket.timesheet_ids = self.ticket.timesheet_ids | timesheet_line
        self.assertTrue(
            self.ticket.timesheet_ids,
            "Helpdesk Ticket: An assigned ticket" "should have a timesheet line now.",
        )
