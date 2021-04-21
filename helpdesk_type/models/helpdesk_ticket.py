# Copyright (c) 2019 Open Source Integrators
# Copyright (C) 2019 Konos
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    type_id = fields.Many2one("helpdesk.ticket.type", string="Type")

    @api.onchange("type_id")
    def _onchange_type_id(self):
        if self.type_id and self.team_id and self.type_id not in self.team_id.type_ids:
            self.team_id = False
            self.user_id = False
