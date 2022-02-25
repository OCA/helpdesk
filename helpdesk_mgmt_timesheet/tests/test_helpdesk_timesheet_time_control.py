# Copyright 2016-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0

from datetime import datetime, timedelta

from odoo import exceptions, fields
from odoo.tests import common


class TestHelpdeskTimesheetTimeControl(common.TransactionCase):
    def setUp(self):
        super().setUp()
        admin = self.browse_ref("base.user_admin")
        # Stop any timer running
        self.env["account.analytic.line"].search(
            [
                ("date_time", "!=", False),
                ("user_id", "=", admin.id),
                ("project_id.allow_timesheets", "=", True),
                ("unit_amount", "=", 0),
            ]
        ).button_end_work()
        admin.groups_id |= self.browse_ref("hr_timesheet.group_hr_timesheet_user")
        self.uid = admin.id
        self.project = self.env["project.project"].create(
            {"name": "Test project", "allow_timesheets": True}
        )
        self.project_without_timesheets = self.env["project.project"].create(
            {"name": "Test project", "allow_timesheets": False}
        )
        self.analytic_account = self.project.analytic_account_id
        self.task = self.env["project.task"].create(
            {"name": "Test task", "project_id": self.project.id}
        )
        team_id = self.env["helpdesk.ticket.team"].create(
            {
                "name": "Team 1",
                "allow_timesheet": True,
                "default_project_id": self.project.id,
            }
        )
        self.ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "team_id": team_id.id,
                "project_id": self.project.id,
                "description": "Test ticket description",
                "user_id": self.uid,
            }
        )
        self.ticket_line = self.env["account.analytic.line"].create(
            {
                "date_time": datetime.now() - timedelta(hours=1),
                "ticket_id": self.ticket.id,
                "project_id": self.project.id,
                "account_id": self.analytic_account.id,
                "name": "Test Ticket Timesheet line",
                "user_id": self.uid,
            }
        )

    def _create_wizard(self, action, active_record):
        """Create a new hr.timesheet.switch wizard in the specified context.
        :param dict action: Action definition that creates the wizard.
        :param active_record: Record being browsed when creating the wizard.
        """
        self.assertEqual(action["res_model"], "hr.timesheet.switch")
        self.assertEqual(action["target"], "new")
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["view_mode"], "form")
        return (
            active_record.env[action["res_model"]]
            .with_context(
                active_id=active_record.id,
                active_ids=active_record.ids,
                active_model=active_record._name,
                **action.get("context", {}),
            )
            .create({})
        )

    def test_ticket_time_control_flow(self):
        """Test project.task time controls."""
        # Running line found, stop the timer
        self.assertEqual(self.ticket.show_time_control, "stop")
        self.ticket.button_end_work()
        # No more running lines, cannot stop again
        with self.assertRaises(exceptions.UserError):
            self.ticket.button_end_work()
        # All lines stopped, start new one
        self.ticket.invalidate_cache()
        self.assertEqual(self.ticket.show_time_control, "start")
        start_action = self.ticket.button_start_work()
        wizard = self._create_wizard(start_action, self.ticket_line)
        self.assertFalse(wizard.amount)
        self.assertLessEqual(wizard.date_time, datetime.now())
        self.assertLessEqual(wizard.date, fields.Date.context_today(wizard))
        self.assertFalse(wizard.unit_amount)
        self.assertEqual(wizard.account_id, self.ticket.project_id.analytic_account_id)
        self.assertEqual(wizard.employee_id, self.env.user.employee_ids)
        self.assertEqual(wizard.name, self.ticket_line.name)
        self.assertEqual(wizard.project_id, self.ticket.project_id)
        self.assertEqual(wizard.ticket_id, self.ticket)
        new_act = wizard.with_context(show_created_timer=True).action_switch()
        new_line = self.env[new_act["res_model"]].browse(new_act["res_id"])
        self.assertEqual(new_line.employee_id, self.env.user.employee_ids)
        self.assertEqual(new_line.project_id, self.project)
        self.assertEqual(new_line.ticket_id, self.ticket)
        self.assertEqual(new_line.unit_amount, 0)
        self.assertTrue(self.ticket_line.unit_amount)
