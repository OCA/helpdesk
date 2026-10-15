# Copyright 2025 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        team_id = res.get("team_id") or self.env.context.get("default_team_id")
        if not team_id:
            return res
        if "user_id" in res and "default_user_id" not in self.env.context:
            res.pop("user_id")
        if (not fields_list or "user_id" in fields_list) and "user_id" not in res:
            team = self.env["helpdesk.ticket.team"].browse(team_id)
            if team.assign_method != "manual":
                res["user_id"] = team.get_new_user().id
        return res

    @api.onchange("team_id")
    def _onchange_team_id(self):
        """Assign user when team changes if not already set."""
        if self.team_id and not self.user_id:
            self.user_id = self.team_id.get_new_user()

    @api.model_create_multi
    def create(self, vals_list):
        """Assign user based on team on creation if not provided."""
        for vals in vals_list:
            team_id = vals.get("team_id")
            if not team_id:
                continue
            team = self.env["helpdesk.ticket.team"].browse(team_id)
            user_id = vals.get("user_id")
            if user_id:
                if user_id not in team.user_ids.ids and team.assign_method != "manual":
                    vals["user_id"] = team.get_new_user().id
            elif team.assign_method != "manual":
                vals["user_id"] = team.get_new_user().id
        return super().create(vals_list)
