from odoo import api, fields, models


class HelpdeskCategory(models.Model):
    _name = "helpdesk.ticket.category"
    _description = "Helpdesk Ticket Category"

    active = fields.Boolean(
        string="Active",
        default=True,
    )
    name = fields.Char(
        string="Name",
        required=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    team_ids = fields.Many2many(
        comodel_name="helpdesk.ticket.team",
        help="""If one or more teams are selected, this category will only
appear to be selectable on tickets whose team is one of those selected.
If a category does not have teams to apply itself on,
it'll appear regardless of the team selected
        """,
        column1="category_id",
        column2="team_id",
        relation="category_team_rel",
        string="Applied on",
    )

    sequence = fields.Integer(string="Sequence")

    @api.model
    def get_categories_by_team(self, team_id) -> list:
        return self.env[self._name].search(
            ["|", ("id", "in", team_id.category_ids.ids), ("team_ids", "=", False)]
        )
