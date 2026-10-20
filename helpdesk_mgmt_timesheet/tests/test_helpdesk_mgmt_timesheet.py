###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
import logging
from datetime import timedelta

from odoo import Command, fields

from odoo.addons.helpdesk_mgmt.tests import test_helpdesk_ticket

_log = logging.getLogger(__name__)


class TestHelpdeskMgmtTimesheet(test_helpdesk_ticket.TestHelpdeskTicket):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
                "group_ids": [
                    Command.set(
                        [cls.env.ref("hr_timesheet.group_hr_timesheet_user").id]
                    )
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

    def test_progress_capped_at_100(self):
        ticket = self.generate_ticket()
        ticket._onchange_team_id()
        ticket.planned_hours = 1
        self.env["account.analytic.line"].with_user(self.user_employee).create(
            {
                "date": fields.Date.today(),
                "name": "Over planned hours",
                "unit_amount": 5,
                "ticket_id": ticket.id,
                "project_id": ticket.project_id.id,
            }
        )
        self.assertEqual(ticket.progress, 100)

    def test_show_time_control_false_without_project_timesheets(self):
        project_no_timesheets = self.env["project.project"].create(
            {"name": "No timesheets project", "allow_timesheets": False}
        )
        ticket = self.generate_ticket()
        ticket.project_id = project_no_timesheets
        self.assertFalse(ticket.show_time_control)

    def test_team_disallow_timesheet_clears_default_project(self):
        self.assertTrue(self.team_id.default_project_id)
        self.team_id.allow_timesheet = False
        self.assertFalse(self.team_id.default_project_id)

    def test_analytic_line_onchange_ticket_id(self):
        ticket = self.generate_ticket()
        line = self.env["account.analytic.line"].new({"ticket_id": ticket.id})
        line.onchange_ticket_id()
        self.assertEqual(line.project_id, ticket.project_id)
        self.assertEqual(line.task_id, ticket.task_id)

    def test_analytic_line_onchange_without_ticket_id(self):
        # no ticket_id set: onchange must be a no-op, not raise
        line = self.env["account.analytic.line"].new({})
        line.onchange_ticket_id()
        self.assertFalse(line.project_id)
