# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import UserError


class HelpdeskTicketSla(models.Model):
    _name = "helpdesk.ticket.sla"
    _description = "Ticket Sla"

    ticket_id = fields.Many2one("helpdesk.ticket", required=True, ondelete="cascade")
    sla_id = fields.Many2one("helpdesk.sla", required=True, ondelete="restrict")
    name = fields.Char(related="sla_id.name")
    color = fields.Integer(compute="_compute_color")
    deadline = fields.Datetime(compute="_compute_deadline", store=True)
    hours = fields.Float(compute="_compute_sla_data", store=True)
    expected_stage_id = fields.Many2one(
        "helpdesk.ticket.stage", compute="_compute_sla_data", store=True
    )
    consumed_time = fields.Float(string="Consumed time", default=0.0, readonly=True)
    last_state_date = fields.Datetime(compute="_compute_sla_data", store=True)
    state = fields.Selection(
        [
            ("accomplished", "Accomplished"),
            ("in_progress", "In Progress"),
            ("expired", "Expired"),
            ("on_hold", "In Hold"),
        ],
        default="accomplished",
        compute="_compute_sla_data",
        store=True,
    )
    expired = fields.Boolean(compute="_compute_expired", search="_search_expired")

    @api.depends("state", "deadline")
    def _compute_expired(self):
        for record in self:
            record.expired = record.state == "expired" or (
                record.state == "in_progress"
                and record.deadline < fields.Datetime.now()
            )

    def _search_expired(self, operator, value):
        if operator not in ["=", "!="]:
            raise UserError(self.env._("Operator is not valid"))
        if (operator == "=" and value) or (operator == "!=" and not value):
            return [
                "|",
                ("state", "=", "expired"),
                "&",
                ("state", "=", "in_progress"),
                ("deadline", "<", fields.Datetime.now()),
            ]
        return [
            "|",
            ("state", "not in", ["expired", "in_progress"]),
            "&",
            ("state", "=", "in_progress"),
            ("deadline", ">=", fields.Datetime.now()),
        ]

    @api.depends("state", "deadline")
    def _compute_color(self):
        for record in self:
            if record.state == "accomplished":
                record.color = 10  # Green
            elif record.state == "expired":
                record.color = 1  # Red
            elif record.state == "in_progress":
                if record.deadline < fields.Datetime.now():
                    record.color = 1  # Red
                else:
                    record.color = 3  # Orange
            else:
                record.color = 0  # Gray

    @api.depends("sla_id")
    def _compute_sla_data(self):
        for record in self:
            record.hours = (
                record.sla_id.hours
                + record.ticket_id.team_id.resource_calendar_id.hours_per_day
                * record.sla_id.days
            )
            record.expected_stage_id = record.sla_id.stage_id
            state = "in_progress"
            if record.ticket_id.stage_id in record.sla_id.ignore_stage_ids:
                state = "on_hold"
            elif (
                record.ticket_id.stage_id.sequence >= record.expected_stage_id.sequence
            ):
                state = "accomplished"
            record.state = state
            record.last_state_date = (
                record.ticket_id.stage_id not in record.sla_id.ignore_stage_ids
                and record.ticket_id.create_date
            )

    @api.depends("hours", "consumed_time", "ticket_id", "last_state_date", "state")
    def _compute_deadline(self):
        for record in self:
            if record.state in ["accomplished", "expired"] and record.deadline:
                # We want to keep the deadline in the past if the SLA is exceeded
                # If it is not defined, it will be recomputed for history
                continue
            else:
                date = record.last_state_date or record.ticket_id.create_date
                date = record.ticket_id.team_id.resource_calendar_id.plan_hours(
                    record.hours - record.consumed_time, date, compute_leaves=True
                )
                record.deadline = date

    def _stage_recompute(self):
        self.ensure_one()
        now = fields.Datetime.now()
        if self.state == "expired":
            return
        deadline = self.deadline
        if self.state == "in_progress":
            calendar = self.ticket_id.team_id.resource_calendar_id
            self.consumed_time += calendar.get_work_hours_count(
                self.last_state_date, now, compute_leaves=True
            )
        if (
            self.state == "accomplished"
            and self.ticket_id.stage_id.sequence < self.expected_stage_id.sequence
        ):
            self.state = "in_progress"
        elif (
            self.state in ["in_progress", "on_hold"]
            and (not deadline or deadline >= now)
            and self.ticket_id.stage_id.sequence >= self.expected_stage_id.sequence
        ):
            self.state = "accomplished"
        elif self.state == "in_progress" and deadline and deadline <= now:
            self.state = "expired"
        if self.state in ["in_progress", "on_hold"]:
            if self.ticket_id.stage_id in self.sla_id.ignore_stage_ids:
                self.state = "on_hold"
            else:
                self.state = "in_progress"
        self.last_state_date = now

    def _check_access(self, operation: str) -> tuple | None:
        result = super()._check_access(operation)
        return result or self.ticket_id._check_access(operation)
