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
        """Return stages applicable to this team.

        Based on company and team assignment.

        Note: In Odoo 19, many2many empty check uses '=' with False.
        For checking specific team assignment, use '=' with single ID.
        """
        if self:
            domain = [
                ("company_id", "in", [False, self.company_id.id]),
                "|",
                ("team_ids", "=", False),
                ("team_ids", "in", self.ids),
            ]
        else:
            domain = [
                ("company_id", "in", [False, self.env.company.id]),
                ("team_ids", "=", False),
            ]
        return self.env["helpdesk.ticket.stage"].search(domain)

    @api.depends("ticket_ids", "ticket_ids.stage_id")
    def _compute_todo_tickets(self):  # noqa: C901
        ticket_model = self.env["helpdesk.ticket"]
        fetch_data = ticket_model._read_group(
            [("team_id", "in", self.ids), ("closed", "=", False)],
            aggregates=["id:count"],
            groupby=["team_id", "user_id", "unattended", "priority"],
        )

        # _read_group can return different shapes across Odoo versions:
        # - tuple/list: (groupby_values..., aggregate_value)
        # - dict: {"team_id": (id, name), ..., "id_count": X}
        # Be defensive and extract ids/values for both formats.
        def _extract_id(val):
            if not val:
                return False
            # recordset
            if hasattr(val, "id"):
                return val.id
            # tuple/list like (id, display_name)
            if isinstance(val, (list, tuple)) and len(val) > 0:
                return val[0]
            # plain int id
            if isinstance(val, int):
                return val
            return False

        def _extract_count(val):
            # aggregate may be an int, or a dict with various keys
            if isinstance(val, int):
                return val
            if isinstance(val, dict):
                # try common keys
                for k in ("id_count", "__count", "count", "id:count"):
                    if k in val and isinstance(val[k], int):
                        return val[k]
                # fallback: first int value
                for v in val.values():
                    if isinstance(v, int):
                        return v
            return 0

        result = []
        for data in fetch_data:
            # tuple/list result
            if isinstance(data, (list, tuple)):
                team_id = _extract_id(data[0])
                user_id = _extract_id(data[1])
                unattended = data[2] if len(data) > 2 and data[2] is not None else False
                priority = data[3] if len(data) > 3 and data[3] is not None else False
                count = _extract_count(data[4]) if len(data) > 4 else 0
                result.append([team_id, user_id, unattended, priority, count])
            elif isinstance(data, dict):
                team_id = _extract_id(data.get("team_id"))
                user_id = _extract_id(data.get("user_id"))
                unattended = data.get("unattended", False)
                priority = data.get("priority", False)
                count = _extract_count(data)
                result.append([team_id, user_id, unattended, priority, count])
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
