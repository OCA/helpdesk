# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    partner_id_domain = fields.Binary(
        help="This is the computed domain to filter partners.",
        compute="_compute_partner_id_domain",
    )

    @api.depends(
        "team_id",
        "team_id.default_partner_id",
        "team_id.allowed_partner_ids",
        "team_id.is_unique_partner",
    )
    def _compute_partner_id_domain(self):
        for record in self:
            if record.team_id:
                if record.team_id.default_partner_id and not record.partner_id:
                    record.partner_id = record.team_id.default_partner_id
                if record.team_id.is_unique_partner:
                    record.partner_id_domain = [
                        ("id", "=", record.team_id.default_partner_id.id)
                    ]
                elif record.team_id.allowed_partner_ids:
                    partners = record.team_id.allowed_partner_ids
                    if record.team_id.default_partner_id:
                        partners |= record.team_id.default_partner_id
                    record.partner_id_domain = [("id", "in", partners.ids)]
                else:
                    record.partner_id_domain = []
            else:
                record.partner_id_domain = []

    @api.constrains("team_id", "partner_id")
    def _check_partner_allowed_by_team(self):
        for record in self:
            if not record.team_id or not record.partner_id:
                continue
            if (
                record.team_id.is_unique_partner
                and record.partner_id != record.team_id.default_partner_id
            ):
                raise ValidationError(
                    _("This partner is not allowed for selected team")
                )
            elif (
                record.team_id.allowed_partner_ids
                and record.partner_id not in record.team_id.allowed_partner_ids
                and record.partner_id != record.team_id.default_partner_id
            ):
                raise ValidationError(
                    _("This partner is not allowed for selected team")
                )
