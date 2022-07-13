#    Copyright (C) 2020 GARCO Consulting <www.garcoconsulting.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo import fields, models


class HelpdeskSla(models.Model):
    _name = "helpdesk.sla"
    _description = "Helpdesk SLA"

    name = fields.Char(string="Name", required=True)
    team_ids = fields.Many2many(comodel_name="helpdesk.ticket.team", string="Teams")
    stage_id = fields.Many2one(comodel_name="helpdesk.ticket.stage", string="Stage")
    days = fields.Integer(string="Days", default=0, required=True)
    hours = fields.Integer(string="Hours", default=0, required=True)
    note = fields.Char(string="Note")
    freeze_stage_ids = fields.Many2many(
        "helpdesk.ticket.stage",
        string="Freezing Stages",
        domain="[('id', '!=', stage_id.id)]",
        help="The amount of time the ticket spends in this stage will be added "
        "to the SLA Policy deadline.",
    )

    def check_sla(self):
        slas = self.search([("team_ids", "!=", False)])
        for sla in slas:
            for team in sla.team_ids:
                if team.ticket_ids:
                    sla.check_ticket_sla(team.ticket_ids)

    def compute_freezed_hours(self, working_calendar, ticket):
        self.ensure_one()
        hours_freezed = 0

        field_stage = self.env["ir.model.fields"]._get(ticket._name, "stage_id")
        freeze_stages = self.freeze_stage_ids.ids

        tracking_lines = ticket.message_ids.tracking_value_ids.filtered(
            lambda tv: tv.field == field_stage
        ).sorted(key="create_date")

        if not tracking_lines:
            return 0

        old_time = ticket.create_date

        for tracking_line in tracking_lines:
            if tracking_line.old_value_integer in freeze_stages:
                hours_freezed += working_calendar.get_work_hours_count(
                    old_time, tracking_line.create_date
                )
            old_time = tracking_line.create_date

        if tracking_lines[-1].new_value_integer in freeze_stages:
            hours_freezed += working_calendar.get_work_hours_count(
                old_time, fields.Datetime.now()
            )

        return hours_freezed

    def check_ticket_sla(self, ticket_ids):
        for ticket in ticket_ids.filtered(lambda t: not t.stage_id.closed):
            deadline = ticket.create_date
            working_calendar = ticket.team_id.resource_calendar_id
            hours = self.hours

            if self.days > 0:
                deadline = working_calendar.plan_days(
                    self.days + 1, deadline, compute_leaves=True
                )
                create_date = ticket.create_date

                deadline = deadline.replace(
                    hour=create_date.hour,
                    minute=create_date.minute,
                    second=create_date.second,
                    microsecond=create_date.microsecond,
                )

                deadline_for_working_cal = working_calendar.plan_hours(0, deadline)

                if (
                    deadline_for_working_cal
                    and deadline.day < deadline_for_working_cal.day
                ):
                    deadline = deadline.replace(
                        hour=0, minute=0, second=0, microsecond=0
                    )

            if self.freeze_stage_ids:
                hours += self.compute_freezed_hours(working_calendar, ticket)

            deadline = working_calendar.plan_hours(hours, deadline, compute_leaves=True)
            ticket.sla_deadline = deadline

            if ticket.sla_deadline < datetime.today().now():
                ticket.sla_expired = True
            else:
                ticket.sla_expired = False
