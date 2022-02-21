#    Copyright (C) 2020 GARCO Consulting <www.garcoconsulting.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    team_sla = fields.Boolean(string="Team SLA", compute="_compute_team_sla")
    sla_expired = fields.Boolean(string="SLA expired")
    sla_deadline = fields.Datetime(string="SLA deadline")

    def _compute_team_sla(self):
        for rec in self:
            rec.team_sla = rec.team_id.use_sla
