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
    name = fields.Char(required=True)
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
        compute="_compute_complete_name", store=True, recursive=True
    )
    parent_path = fields.Char(index=True)

    @api.depends("name", "parent_id.complete_name")
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
        fetch_data = ticket_model.read_group(
            [("team_id", "in", self.ids), ("closed", "=", False)],
            ["team_id", "user_id", "unattended", "priority"],
            ["team_id", "user_id", "unattended", "priority"],
            lazy=False,
        )
        result = [
            [
                data["team_id"][0],
                data["user_id"] and data["user_id"][0],
                data["unattended"],
                data["priority"],
                data["__count"],
            ]
            for data in fetch_data
        ]
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
