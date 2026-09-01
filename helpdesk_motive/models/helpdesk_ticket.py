# Copyright (c) 2019 Open Source Integrators
# Copyright (C) 2019 Konos
# Copyright (C) 2023 Binhex -Adasat Torres
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    motive_id = fields.Many2one(
        "helpdesk.ticket.motive",
        string="Motive",
        store=True,
        readonly=False,
        compute="_compute_team_user_helpdesk_motive",
    )

    @api.depends("team_id", "user_id")
    def _compute_team_user_helpdesk_motive(self):
        for record in self:
            record.motive_id = False
