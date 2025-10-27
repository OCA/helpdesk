# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not self.env.user.share or not vals.get("category_id"):
                continue

            category = self.env["helpdesk.ticket.category"].browse(
                vals.get("category_id")
            )

            if not category.default_partner_id:
                continue

            if not self.env.company.helpdesk_mgmt_portal_select_team or not vals.get(
                "team_id"
            ):
                vals["user_id"] = category.default_partner_id.id
                continue

            team = self.env["helpdesk.ticket.team"].browse(vals.get("team_id"))

            if team and category.default_partner_id in team.user_ids:
                vals["user_id"] = category.default_partner_id.id
                continue

        return super().create(vals_list)
