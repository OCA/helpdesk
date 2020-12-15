# Copyright 2020 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class HelpdeskTicket(models.Model):
    _name = "helpdesk.ticket"
    _inherit = ["helpdesk.ticket", "hr.timesheet.time_control.mixin"]

    @api.model
    def _relation_with_timesheet_line(self):
        return "ticket_id"

    @api.depends(
        "team_id.allow_timesheet",
        "project_id.allow_timesheets",
        "timesheet_ids.employee_id",
        "timesheet_ids.unit_amount",
    )
    def _compute_show_time_control(self):
        result = super()._compute_show_time_control()
        for ticket in self:
            if not (
                ticket.project_id.allow_timesheets and ticket.team_id.allow_timesheet
            ):
                ticket.show_time_control = False
        return result

    def button_start_work(self):
        result = super().button_start_work()
        result["context"].update(
            {
                "default_project_id": self.project_id.id,
                "default_task_id": self.task_id.id,
            }
        )
        return result
