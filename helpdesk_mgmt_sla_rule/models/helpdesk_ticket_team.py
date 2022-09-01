# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HelpDeskTicketTeam(models.Model):
    _inherit = "helpdesk.ticket.team"

    use_sla_rule = fields.Boolean(
        string="Use SLA Rule", help="Use SLA Rules for this team."
    )
