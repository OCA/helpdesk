# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class HelpdeskTicketTeam(models.Model):
    _inherit = "helpdesk.ticket.team"

    default_partner_id = fields.Many2one(
        comodel_name="res.partner",
    )
    is_unique_partner = fields.Boolean()
    allowed_partner_ids = fields.Many2many(
        comodel_name="res.partner",
    )

    @api.onchange("default_partner_id")
    def _onchange_default_partner_id(self):
        for record in self.filtered(lambda x: not x.default_partner_id):
            record.is_unique_partner = False
