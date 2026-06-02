from odoo import fields, models


class HelpdeskTicketTeamAssignmentTag(models.Model):
    _name = "helpdesk.ticket.team.assignment.tag"
    _description = "Helpdesk Team Tag Assignment"

    team_id = fields.Many2one(
        comodel_name="helpdesk.ticket.team",
        string="Team",
        required=True,
        ondelete="cascade",
    )
    tag_id = fields.Many2one(
        comodel_name="helpdesk.ticket.tag",
        string="Tag",
        required=True,
        ondelete="cascade",
    )
    user_ids = fields.Many2many(
        comodel_name="res.users",
        string="Members",
        help="Members eligible to be auto-assigned tickets carrying this tag.",
    )

    _team_tag_uniq = models.Constraint(
        "unique(team_id, tag_id)",
        "A tag can only be mapped once per team.",
    )
