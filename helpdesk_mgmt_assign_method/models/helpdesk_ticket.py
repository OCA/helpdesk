# Copyright 2025 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    @api.model
    def default_get(self, fields_list):
        """Assign user based on team when creating a new ticket."""
        res = super().default_get(fields_list)
        team_id = res.get("team_id")
        if (
            (not fields_list or "user_id" in fields_list)
            and "user_id" not in res
            and team_id
        ):
            team = self.env["helpdesk.ticket.team"].browse(team_id)
            res["user_id"] = team.get_new_user().id
        return res

    @api.onchange("team_id")
    def _onchange_team_id(self):
        """Assign user when team changes if not already set."""
        if self.team_id and not self.user_id:
            self.user_id = self.team_id.get_new_user()

    @api.model
    def create(self, vals):
        """Assign user based on team on creation if not provided."""
        team_id = vals.get("team_id")
        if team_id and not vals.get("user_id"):
            team = self.env["helpdesk.ticket.team"].browse(team_id)
            vals["user_id"] = team.get_new_user().id
        return super().create(vals)
