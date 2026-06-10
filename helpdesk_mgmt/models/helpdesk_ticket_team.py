import datetime

import pytz
from dateutil import relativedelta

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class HelpdeskTeam(models.Model):
    _name = "helpdesk.ticket.team"
    _description = "Helpdesk Ticket Team"
    _inherit = ["mail.thread", "mail.alias.mixin"]
    _order = "sequence, id"
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = "name"
    _rec_name = "complete_name"

    sequence = fields.Integer(default=10)
    name = fields.Char(required=True, translate=True)
    user_ids = fields.Many2many(
        comodel_name="res.users",
        string="Members",
        relation="helpdesk_ticket_team_res_users_rel",
        column1="helpdesk_ticket_team_id",
        column2="res_users_id",
    )
    active = fields.Boolean(default=True)
    category_ids = fields.Many2many(
        comodel_name="helpdesk.ticket.category", string="Category"
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Team Leader",
        check_company=True,
    )
    alias_id = fields.Many2one(
        comodel_name="mail.alias",
        string="Email",
        ondelete="restrict",
        required=True,
        help="The email address associated with "
        "this channel. New emails received will "
        "automatically create new tickets assigned "
        "to the channel.",
    )
    color = fields.Integer(string="Color Index", default=0)
    ticket_ids = fields.One2many(
        comodel_name="helpdesk.ticket",
        inverse_name="team_id",
        string="Tickets",
    )
    todo_ticket_count = fields.Integer(
        string="Number of tickets", compute="_compute_todo_tickets"
    )
    todo_ticket_count_unassigned = fields.Integer(
        string="Number of tickets unassigned", compute="_compute_todo_tickets"
    )
    todo_ticket_count_unattended = fields.Integer(
        string="Number of tickets unattended", compute="_compute_todo_tickets"
    )
    todo_ticket_count_high_priority = fields.Integer(
        string="Number of tickets in high priority", compute="_compute_todo_tickets"
    )
    open_ticket_count = fields.Integer(
        string="Open Tickets", compute="_compute_open_ticket_count"
    )
    unassigned_tickets = fields.Integer(compute="_compute_unassigned_tickets")
    urgent_ticket = fields.Integer(
        string="Urgent Tickets", compute="_compute_urgent_ticket"
    )
    ticket_closed = fields.Integer(
        string="Tickets Closed (7 days)", compute="_compute_ticket_closed"
    )
    show_in_portal = fields.Boolean(
        string="Show in portal form",
        default=True,
        help="Allow to select this team when creating a new ticket in the portal.",
    )
    parent_id = fields.Many2one(
        "helpdesk.ticket.team", string="Parent Team", index=True
    )
    complete_name = fields.Char(
        compute="_compute_complete_name",
        recursive=True,
        search="_search_complete_name",
    )
    parent_path = fields.Char(index=True)

    def _search_complete_name(self, operator, value):
        records = self.search_fetch([], ["complete_name"]).filtered_domain(
            [("complete_name", operator, value)]
        )
        return [("id", "in", records.ids)]

    @api.depends("name", "parent_id.complete_name")
    @api.depends_context("lang")
    def _compute_complete_name(self):
        for record in self:
            if record.parent_id:
                record.complete_name = (
                    f"{record.parent_id.complete_name} / {record.name}"
                )
            else:
                record.complete_name = record.name

    def _get_applicable_stages(self):
        if self:
            domain = [
                ("company_id", "in", [False, self.company_id.id]),
                "|",
                ("team_ids", "=", False),
                ("team_ids", "=", self.id),
            ]
        else:
            domain = [
                ("company_id", "in", [False, self.env.company.id]),
                ("team_ids", "=", False),
            ]
        return self.env["helpdesk.ticket.stage"].search(domain)

    @api.depends("ticket_ids", "ticket_ids.stage_id")
    def _compute_todo_tickets(self):
        ticket_model = self.env["helpdesk.ticket"]
        result = []
        grouped_rows = ticket_model._read_group(
            domain=[("team_id", "in", self.ids), ("closed", "=", False)],
            groupby=["team_id", "user_id", "unattended", "priority"],
            aggregates=["__count"],
        )
        for team, user, unattended, priority, count in grouped_rows:
            result.append(
                [
                    team.id if team else False,
                    user.id if user else False,
                    unattended,
                    priority,
                    count,
                ]
            )
        for team in self:
            team.todo_ticket_count = sum(r[4] for r in result if r[0] == team.id)
            team.todo_ticket_count_unassigned = sum(
                r[4] for r in result if r[0] == team.id and not r[1]
            )
            team.todo_ticket_count_unattended = sum(
                r[4] for r in result if r[0] == team.id and r[2]
            )
            team.todo_ticket_count_high_priority = sum(
                r[4] for r in result if r[0] == team.id and r[3] == "3"
            )

    @api.depends("ticket_ids", "ticket_ids.closed")
    def _compute_open_ticket_count(self):
        ticket_data = self.env["helpdesk.ticket"]._read_group(
            [("team_id", "in", self.ids), ("closed", "=", False)],
            ["team_id"],
            ["__count"],
        )
        mapped = {team.id: count for team, count in ticket_data}
        for team in self:
            team.open_ticket_count = mapped.get(team.id, 0)

    @api.depends("ticket_ids", "ticket_ids.user_id", "ticket_ids.closed")
    def _compute_unassigned_tickets(self):
        ticket_data = self.env["helpdesk.ticket"]._read_group(
            [
                ("team_id", "in", self.ids),
                ("user_id", "=", False),
                ("closed", "=", False),
            ],
            ["team_id"],
            ["__count"],
        )
        mapped = {team.id: count for team, count in ticket_data}
        for team in self:
            team.unassigned_tickets = mapped.get(team.id, 0)

    @api.depends("ticket_ids", "ticket_ids.priority", "ticket_ids.closed")
    def _compute_urgent_ticket(self):
        ticket_data = self.env["helpdesk.ticket"]._read_group(
            [
                ("team_id", "in", self.ids),
                ("closed", "=", False),
                ("priority", "=", "3"),
            ],
            ["team_id"],
            ["__count"],
        )
        mapped = {team.id: count for team, count in ticket_data}
        for team in self:
            team.urgent_ticket = mapped.get(team.id, 0)

    @api.depends("ticket_ids", "ticket_ids.closed_date", "ticket_ids.closed")
    def _compute_ticket_closed(self):
        dt = datetime.datetime.combine(
            datetime.date.today() - relativedelta.relativedelta(days=6),
            datetime.time.min,
        )
        ticket_data = self.env["helpdesk.ticket"]._read_group(
            [
                ("team_id", "in", self.ids),
                ("closed", "=", True),
                ("closed_date", ">=", dt),
            ],
            ["team_id"],
            ["__count"],
        )
        mapped = {team.id: count for team, count in ticket_data}
        for team in self:
            team.ticket_closed = mapped.get(team.id, 0)

    def _alias_get_creation_values(self):
        values = super()._alias_get_creation_values()
        values["alias_model_id"] = self.env.ref(
            "helpdesk_mgmt.model_helpdesk_ticket"
        ).id
        values["alias_defaults"] = defaults = safe_eval(self.alias_defaults or "{}")
        defaults["team_id"] = self.id
        return values

    # ---------------------------------------------------
    # Overview (agent metrics + team drill-downs)
    # ---------------------------------------------------

    _OVERVIEW_PRIORITY_HIGH = "2"
    _OVERVIEW_PRIORITY_URGENT = "3"

    @api.model
    def _overview_sample_payload(self):
        return {
            "sample_mode": True,
            "assigned_open": {
                "any": {"ticket_count": 7, "mean_open_hours": 24.0},
                "high": {"ticket_count": 2, "mean_open_hours": 8.5},
                "urgent": {"ticket_count": 1, "mean_open_hours": 11.0},
            },
            "assigned_closed": {"today": 2, "last_7_days": 11},
        }

    @api.model
    def _overview_user_day_start_utc(self):
        """Beginning of the user's local calendar day as a naive UTC datetime."""
        tz_name = self.env.user.tz or "UTC"
        user_tz = pytz.timezone(tz_name)
        local_now = datetime.datetime.now(user_tz)
        local_start = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
        return local_start.astimezone(pytz.UTC).replace(tzinfo=None)

    @api.model
    def _overview_empty_open_buckets(self):
        empty = {"ticket_count": 0, "mean_open_hours": 0.0}
        return {"any": dict(empty), "high": dict(empty), "urgent": dict(empty)}

    @api.model
    def _overview_aggregate_assigned_open(self, ticket_model):
        buckets = self._overview_empty_open_buckets()
        rows = ticket_model._read_group(
            [
                ("user_id", "=", self.env.uid),
                ("closed", "=", False),
            ],
            groupby=["priority"],
            aggregates=["open_hours:sum", "__count"],
        )
        for priority, hours_sum, ticket_count in rows:
            priority_key = priority or "0"
            hours_sum = hours_sum or 0.0
            buckets["any"]["ticket_count"] += ticket_count
            buckets["any"]["mean_open_hours"] += hours_sum
            if priority_key == self._OVERVIEW_PRIORITY_HIGH:
                buckets["high"]["ticket_count"] = ticket_count
                buckets["high"]["mean_open_hours"] = hours_sum
            elif priority_key == self._OVERVIEW_PRIORITY_URGENT:
                buckets["urgent"]["ticket_count"] = ticket_count
                buckets["urgent"]["mean_open_hours"] = hours_sum
        for key in ("any", "high", "urgent"):
            count = buckets[key]["ticket_count"]
            buckets[key]["mean_open_hours"] = fields.Float.round(
                buckets[key]["mean_open_hours"] / (count or 1), 2
            )
        return buckets

    @api.model
    def _overview_count_assigned_closed(self, ticket_model, *, since):
        return ticket_model.search_count(
            [
                ("user_id", "=", self.env.uid),
                ("closed", "=", True),
                ("closed_date", ">=", since),
            ]
        )

    @api.model
    def fetch_agent_overview(self):
        """Metrics for the overview banner of the current agent."""
        ticket_model = self.env["helpdesk.ticket"]
        if not ticket_model.search_count([]):
            return self._overview_sample_payload()
        day_start = self._overview_user_day_start_utc()
        week_start = day_start - datetime.timedelta(days=6)
        return {
            "sample_mode": False,
            "assigned_open": self._overview_aggregate_assigned_open(ticket_model),
            "assigned_closed": {
                "today": self._overview_count_assigned_closed(
                    ticket_model, since=day_start
                ),
                "last_7_days": self._overview_count_assigned_closed(
                    ticket_model, since=week_start
                ),
            },
        }

    def _overview_team_ticket_window(self, *, closed=False, extra_context=None):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "helpdesk_mgmt.helpdesk_ticket_action_team"
        )
        action["display_name"] = self.name
        context = {
            "search_default_open": 0 if closed else 1,
            "default_team_id": self.id,
        }
        if extra_context:
            context.update(extra_context)
        domain = [("team_id", "in", self.ids)]
        if closed:
            week_start = self._overview_user_day_start_utc() - datetime.timedelta(
                days=6
            )
            domain += [("closed", "=", True), ("closed_date", ">=", week_start)]
            context["search_default_closed_last_7_days"] = 1
        action.update({"domain": domain, "context": context})
        return action

    def action_overview_open_team_tickets(self):
        self.ensure_one()
        return self._overview_team_ticket_window()

    def action_overview_team_open_tickets(self):
        self.ensure_one()
        return self._overview_team_ticket_window()

    def action_overview_team_closed_week(self):
        self.ensure_one()
        return self._overview_team_ticket_window(closed=True)

    def action_overview_team_urgent_tickets(self):
        self.ensure_one()
        return self._overview_team_ticket_window(
            extra_context={"search_default_urgent_priority": 1}
        )
