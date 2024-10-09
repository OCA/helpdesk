#    Copyright (C) 2020 GARCO Consulting <www.garcoconsulting.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HelpdeskTicketTeam(models.Model):
    _inherit = "helpdesk.ticket.team"

    use_sla = fields.Boolean(string="Use SLA")
    resource_calendar_id = fields.Many2one(
        "resource.calendar",
        "Working Hours",
        default=lambda self: self.env.company.resource_calendar_id,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )
