###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
import logging
from datetime import timedelta

from odoo import fields

from odoo.addons.helpdesk_mgmt.tests import test_helpdesk_ticket

_log = logging.getLogger(__name__)


class TestHelpdeskMgmtTimesheet(test_helpdesk_ticket.TestHelpdeskTicket):
    @classmethod
    def setUpClass(cls):
        super(TestHelpdeskMgmtTimesheet, cls).setUpClass()
        cls.project_id = cls.env["project.project"].create({"name": "Project"})
        cls.team_id = cls.env["helpdesk.ticket.team"].create(
            {
                "name": "Team 1",
                "allow_timesheet": True,
                "default_project_id": cls.project_id.id,
            }
        )
        # users
        cls.user_employee = cls.env["res.users"].create(
            {
                "name": "User Employee",
                "login": "user_employee",
                "email": "useremployee@test.com",
                "groups_id": [
                    (6, 0, [cls.env.ref("hr_timesheet.group_hr_timesheet_user").id])
                ],
            }
        )
        # employees
        cls.empl_employee = cls.env["hr.employee"].create(
            {
                "name": "User Empl Employee",
                "user_id": cls.user_employee.id,
            }
        )

    def generate_ticket(self):
        return self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket 1",
                "description": "Test ticket description",
                "team_id": self.team_id.id,
            }
        )

    def test_helpdesk_mgmt_timesheet(self):
        Timesheet = self.env["account.analytic.line"]
        ticket = self.generate_ticket()
        self.assertFalse(ticket.last_timesheet_activity)
        ticket._onchange_team_id()
        self.assertEqual(ticket.project_id.id, self.team_id.default_project_id.id)
        ticket.planned_hours = 5
        days_ago = 1
        timesheet1 = Timesheet.with_user(self.user_employee).create(
            {
                "date": fields.Date.today() - timedelta(days=days_ago),
                "name": "Test Timesheet",
                "unit_amount": 2,
                "ticket_id": ticket.id,
                "project_id": ticket.project_id.id,
            }
        )
        self.assertEqual(
            ticket.last_timesheet_activity,
            fields.Date.today() - timedelta(days=days_ago),
        )
        timesheet2 = Timesheet.with_user(self.user_employee).create(
            {
                "date": fields.Date.today() - timedelta(days=0),
                "name": "Test Timesheet",
                "unit_amount": 1,
                "ticket_id": ticket.id,
                "project_id": ticket.project_id.id,
            }
        )
        self.assertEqual(ticket.last_timesheet_activity, fields.Date.today())
        self.assertEqual(
            ticket.total_hours, timesheet1.unit_amount + timesheet2.unit_amount
        )
        self.assertEqual(
            ticket.remaining_hours, ticket.planned_hours - ticket.total_hours
        )
