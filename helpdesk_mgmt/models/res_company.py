# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    helpdesk_mgmt_portal_select_team = fields.Boolean(
        string="Select team in Helpdesk portal"
    )
