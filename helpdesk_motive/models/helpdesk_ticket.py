# Copyright (c) 2019 Open Source Integrators
# Copyright (C) 2019 Konos
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    motive_id = fields.Many2one(
        "helpdesk.ticket.motive", string="Motive", help="Motive"
    )

    @api.onchange("team_id", "user_id")
    def _onchange_team_user_helpdesk_motive(self):
        for record in self:
            record.motive_id = False
