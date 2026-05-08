# Copyright 2016-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0

from datetime import datetime, timedelta

from odoo import Command, exceptions
from odoo.tests import common


class TestHelpdeskTimesheetTimeControl(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        admin = cls.env.ref("base.user_admin")
        # Stop any timer running
        cls.env["account.analytic.line"].search(
            [
                ("date_time", "!=", False),
                ("user_id", "=", admin.id),
                ("project_id.allow_timesheets", "=", True),
                ("unit_amount", "=", 0),
            ]
        ).button_end_work()
        admin.write(
            {
                "group_ids": [
                    Command.link(cls.env.ref("hr_timesheet.group_hr_timesheet_user").id)
                ]
            }
        )
        cls.uid = admin.id
        cls.project = cls.env["project.project"].create(
            {"name": "Test project", "allow_timesheets": True}
        )
        cls.project_without_timesheets = cls.env["project.project"].create(
            {"name": "Test project", "allow_timesheets": False}
        )
        cls.analytic_account = cls.project.account_id
        cls.task = cls.env["project.task"].create(
            {"name": "Test task", "project_id": cls.project.id}
        )
        team_id = cls.env["helpdesk.ticket.team"].create(
            {
                "name": "Team 1",
                "allow_timesheet": True,
                "default_project_id": cls.project.id,
            }
        )
        cls.ticket = cls.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "team_id": team_id.id,
                "project_id": cls.project.id,
                "description": "Test ticket description",
                "user_id": cls.uid,
            }
        )
        cls.ticket_line = cls.env["account.analytic.line"].create(
            {
                "date_time": datetime.now() - timedelta(hours=1),
                "ticket_id": cls.ticket.id,
                "project_id": cls.project.id,
                "account_id": cls.analytic_account.id,
                "name": "Test Ticket Timesheet line",
                "user_id": cls.uid,
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
        self.ticket.invalidate_recordset()
        self.assertEqual(self.ticket.show_time_control, "start")
        start_action = self.ticket.button_start_work()
        wizard = self._create_wizard(start_action, self.ticket_line)
        self.assertLessEqual(wizard.date_time, datetime.now())
        self.assertEqual(wizard.name, self.ticket_line.name)
        self.assertEqual(wizard.project_id, self.ticket.project_id)
        new_act = wizard.with_context(show_created_timer=True).action_switch()
        new_line = self.env[new_act["res_model"]].browse(new_act["res_id"])
        self.assertEqual(new_line.employee_id, self.env.user.employee_ids)
        self.assertEqual(new_line.project_id, self.project)
        self.assertEqual(new_line.ticket_id, self.ticket)
        self.assertEqual(new_line.unit_amount, 0)
        self.assertTrue(self.ticket_line.unit_amount)
