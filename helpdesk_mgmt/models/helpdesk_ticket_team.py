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
        help="The email address associated with \
                               this channel. New emails received will \
                               automatically create new tickets assigned \
                               to the channel.",
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
    show_in_portal = fields.Boolean(
        string="Show in portal form",
        default=True,
        help="Allow to select this team when creating a new ticket in the portal.",
    )
    parent_id = fields.Many2one(
        "helpdesk.ticket.team", string="Parent Team", index=True
    )
    assign_method = fields.Selection(
        selection=[
            ("manual", "Manually"),
            ("randomly", "Random (round-robin)"),
            ("balanced", "Balanced (least busy)"),
            ("tags", "By Tags"),
        ],
        string="Assignment Method",
        default="manual",
        required=True,
        tracking=True,
        help="How new unassigned tickets of this team get an assigned user:\n"
        "- Manually: no automatic assignment.\n"
        "- Random: rotate cyclically over the team members.\n"
        "- Balanced: assign to the member with the fewest open tickets.\n"
        "- By Tags: assign to a member mapped to the ticket tags, "
        "picking the least busy one.",
    )
    assignment_tag_ids = fields.One2many(
        comodel_name="helpdesk.ticket.team.assignment.tag",
        inverse_name="team_id",
        string="Tag Assignments",
        help="Mapping between ticket tags and the members eligible to be "
        "auto-assigned when the 'By Tags' method is used.",
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

    # ---------------------------------------------------
    # Auto-assignment
    # ---------------------------------------------------

    def _get_auto_assign_user(self, tag_ids=None):
        """Return the member that should take a new ticket of this team.

        The selection depends on ``assign_method``. Returns an empty
        ``res.users`` recordset when no member can be picked (manual method,
        team without members, or no tag mapping match).
        """
        self.ensure_one()
        members = self.user_ids
        if not members or self.assign_method == "manual":
            return self.env["res.users"]
        if self.assign_method == "randomly":
            return self._auto_assign_randomly(members)
        if self.assign_method == "balanced":
            return self._auto_assign_balanced(members)
        if self.assign_method == "tags":
            return self._auto_assign_by_tags(members, tag_ids or [])
        return self.env["res.users"]

    def _auto_assign_randomly(self, members):
        """Round-robin: pick the member right after the last assigned one."""
        members = members.sorted("id")
        last_ticket = self.env["helpdesk.ticket"].search(
            [
                ("team_id", "=", self.id),
                ("user_id", "in", members.ids),
            ],
            order="assigned_date desc, id desc",
            limit=1,
        )
        if not last_ticket:
            return members[0]
        member_ids = members.ids
        next_index = (member_ids.index(last_ticket.user_id.id) + 1) % len(member_ids)
        return members[next_index]

    def _auto_assign_balanced(self, members):
        """Balanced: pick the member with the fewest open tickets."""
        counts = dict.fromkeys(members.ids, 0)
        grouped_rows = self.env["helpdesk.ticket"]._read_group(
            domain=[
                ("team_id", "=", self.id),
                ("user_id", "in", members.ids),
                ("closed", "=", False),
            ],
            groupby=["user_id"],
            aggregates=["__count"],
        )
        for user, count in grouped_rows:
            counts[user.id] = count
        # Tie-break by member id to keep the choice deterministic.
        best_id = min(members.ids, key=lambda uid: (counts[uid], uid))
        return members.browse(best_id)

    def _auto_assign_by_tags(self, members, tag_ids):
        """By tags: restrict to members mapped to the ticket tags, then
        fall back to the balanced strategy among that pool."""
        if not tag_ids:
            return self.env["res.users"]
        mappings = self.assignment_tag_ids.filtered(lambda m: m.tag_id.id in tag_ids)
        candidates = mappings.user_ids & members
        if not candidates:
            return self.env["res.users"]
        return self._auto_assign_balanced(candidates)

    def _alias_get_creation_values(self):
        values = super()._alias_get_creation_values()
        values["alias_model_id"] = self.env.ref(
            "helpdesk_mgmt.model_helpdesk_ticket"
        ).id
        values["alias_defaults"] = defaults = safe_eval(self.alias_defaults or "{}")
        defaults["team_id"] = self.id
        return values

    @api.model
    def retrieve_dashboard(self):
        return sorted(self._retrieve_dashboard(), key=lambda d: d.get("sequence", 99))

    def _retrieve_dashboard(self):
        no_team_tickets = self.env["helpdesk.ticket"].search_count(
            [("team_id", "=", False), ("stage_id.closed", "=", False)]
        )
        return [
            {
                "name": self.env._("Open Tickets without team"),
                "value": no_team_tickets,
                "sequence": 1,
                "icon": "fa-exclamation-circle",
                "show": no_team_tickets > 0,
                "action": "helpdesk_mgmt.helpdesk_ticket_action_unassigned",
            },
            {
                "name": self.env._("Open Tickets"),
                "value": self.env["helpdesk.ticket"].search_count(
                    [("stage_id.closed", "=", False)]
                ),
                "sequence": 2,
                "icon": "fa-life-ring",
                "show": True,
                "action": "helpdesk_mgmt.helpdesk_ticket_action_opened",
            },
        ]
