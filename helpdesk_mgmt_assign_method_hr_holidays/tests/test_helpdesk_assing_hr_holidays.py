from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import Command

from odoo.addons.hr_holidays.tests.common import TestHrHolidaysCommon


class TestHelpdeskTicketAssignHolidays(TestHrHolidaysCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_1 = cls.env["res.users"].create(
            {"name": "User 1", "login": "user1@example.com"}
        )
        cls.user_1_emp = cls.env["hr.employee"].create(
            {
                "name": "User",
                "user_id": cls.user_1.id,
                "department_id": cls.rd_dept.id,
            }
        )
        cls.user_2 = cls.env["res.users"].create(
            {"name": "User 2", "login": "user2@example.com"}
        )
        cls.user_2_emp = cls.env["hr.employee"].create(
            {
                "name": "User",
                "user_id": cls.user_2.id,
                "department_id": cls.rd_dept.id,
            }
        )

        cls.team = cls.env["helpdesk.ticket.team"].create(
            {
                "name": "Team",
                "user_ids": [Command.set([cls.user_1.id, cls.user_2.id])],
                "assign_method": "balanced",
            }
        )
        cls.leave_type = cls.env["hr.leave.type"].create(
            {
                "name": "Paid Time Off",
                "time_type": "leave",
                "requires_allocation": "yes",
                "allocation_validation_type": "officer",
            }
        )

    def _create_ticket(self, **extra):
        vals = {
            "name": "Test Ticket",
            "description": "Test description",
            "team_id": self.team.id,
            **extra,
        }
        return self.env["helpdesk.ticket"].create(vals)

    def test_users_on_leave_not_assigned(self):
        self._create_ticket(user_id=self.user_2.id)
        self._create_test_allocation(
            self.leave_type, "2020-01-01", self.user_1.employee_id, number_of_days=5
        ).action_validate()
        self._take_leave_and_validate(
            self.user_1.employee_id,
            self.leave_type,
            date_from=date.today(),
            date_to=date.today() + relativedelta(days=1),
        )
        self.assertEqual(self.team._get_available_users(), self.user_2)
        ticket_2 = self._create_ticket()
        self.assertEqual(ticket_2.user_id, self.user_2)
