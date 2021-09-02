###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, fields, models


class HelpdeskTicket(models.Model):
    _name = "helpdesk.ticket"
    _inherit = ["helpdesk.ticket", "hr.timesheet.time_control.mixin"]

    @api.model
    def _relation_with_timesheet_line(self):
        return "ticket_id"

    allow_timesheet = fields.Boolean(
        string="Allow Timesheet",
        related="team_id.allow_timesheet",
    )
    planned_hours = fields.Float(string="Planned Hours", tracking=True)
    progress = fields.Float(
        compute="_compute_progress_hours",
        group_operator="avg",
        store=True,
        string="Progress",
    )
    remaining_hours = fields.Float(
        compute="_compute_progress_hours",
        readonly=True,
        store=True,
        string="Remaining Hours",
    )
    timesheet_ids = fields.One2many(
        comodel_name="account.analytic.line",
        inverse_name="ticket_id",
        string="Timesheet",
    )
    total_hours = fields.Float(
        compute="_compute_total_hours", readonly=True, store=True, string="Total Hours"
    )
    last_timesheet_activity = fields.Date(
        compute="_compute_last_timesheet_activity",
        readonly=True,
        store=True,
    )

    @api.depends("timesheet_ids.unit_amount")
    def _compute_total_hours(self):
        for record in self:
            record.total_hours = sum(record.timesheet_ids.mapped("unit_amount"))

    @api.constrains("project_id")
    def _constrains_project_timesheets(self):
        for record in self:
            record.timesheet_ids.update({"project_id": record.project_id.id})

    @api.onchange("team_id")
    def _onchange_team_id(self):
        for record in self.filtered(lambda a: a.team_id and a.team_id.allow_timesheet):
            record.project_id = record.team_id.default_project_id

    @api.depends("planned_hours", "total_hours")
    def _compute_progress_hours(self):
        for ticket in self:
            ticket.progress = 0.0
            if ticket.planned_hours > 0.0:
                if ticket.total_hours > ticket.planned_hours:
                    ticket.progress = 100
                else:
                    ticket.progress = round(
                        100.0 * ticket.total_hours / ticket.planned_hours, 2
                    )
            ticket.remaining_hours = ticket.planned_hours - ticket.total_hours

    @api.depends("timesheet_ids.date")
    def _compute_last_timesheet_activity(self):
        for record in self:
            record.last_timesheet_activity = (
                record.timesheet_ids
                and record.timesheet_ids.sorted(key="date", reverse=True)[0].date
            ) or False

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
