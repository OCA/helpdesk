# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class HelpdeskTicketTeam(models.Model):
    _inherit = "helpdesk.ticket.team"

    motive_ids = fields.One2many(
        comodel_name="helpdesk.ticket.motive", inverse_name="team_id", string="Motives"
    )
