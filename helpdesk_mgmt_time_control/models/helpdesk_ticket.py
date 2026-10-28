###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, models


class HelpdeskTicket(models.Model):
    _name = "helpdesk.ticket"
    _inherit = ["helpdesk.ticket", "hr.timesheet.time_control.mixin"]

    @api.depends(
        "team_id.allow_timesheet",
        "project_id.allow_timesheets",
        "timesheet_ids.employee_id",
        "timesheet_ids.unit_amount",
    )
    def _compute_show_time_control(self):
        result = super()._compute_show_time_control()
        for ticket in self:
            # We use sudo() for the project because the ticket user may not have
            # permission to access it—for example, if the project is visible to
            # invited internal users and the ticket user is not one of them
            if not (
                ticket.project_id.sudo().allow_timesheets
                and ticket.team_id.allow_timesheet
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
