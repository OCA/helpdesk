# Copyright (c) 2019 Open Source Integrators
# Copyright (C) 2019 Konos
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    type_id = fields.Many2one("helpdesk.ticket.type", string="Type")

    @api.onchange("type_id")
    def _onchange_type_id(self):
        valid_team_ids = self.type_id.team_ids
        if self.type_id and self.team_id not in valid_team_ids:
            self.team_id = len(valid_team_ids) == 1 and valid_team_ids
            self.user_id = False
