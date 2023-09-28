# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    helpdesk_mgmt_portal_select_team = fields.Boolean(
        related="company_id.helpdesk_mgmt_portal_select_team",
        readonly=False,
    )
    helpdesk_mgmt_portal_team_id_required = fields.Boolean(
        related="company_id.helpdesk_mgmt_portal_team_id_required",
        readonly=False,
    )
    helpdesk_mgmt_portal_category_id_required = fields.Boolean(
        related="company_id.helpdesk_mgmt_portal_category_id_required",
        readonly=False,
    )
