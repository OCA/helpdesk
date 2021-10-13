# Copyright 2021 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HelpdeskCategory(models.Model):
    _inherit = "helpdesk.ticket.category"

    is_available_rest_api = fields.Boolean(
        string="Is available from REST API", default=False
    )


class HelpdeskTeam(models.Model):
    _inherit = "helpdesk.ticket.team"

    is_available_rest_api = fields.Boolean(
        string="Is available from REST API", default=False
    )
