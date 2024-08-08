# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import ast

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    helpdesk_available_model_ids = fields.Many2many(
        comodel_name="ir.model",
        domain="[('transient', '=', False)]",
        string="Available Models",
        help="Available models for set source record in helpdesk ticket",
    )

    def set_values(self):
        super().set_values()
        ICPSudo = self.env["ir.config_parameter"].sudo()
        ICPSudo.set_param(
            "helpdesk_mgmt_activity.helpdesk_available_model_ids",
            str(self.helpdesk_available_model_ids.ids),
        )
        return

    @api.model
    def get_values(self):
        res = super().get_values()
        ICPSudo = self.env["ir.config_parameter"].sudo()
        helpdesk_available_model_ids = ICPSudo.get_param(
            "helpdesk_mgmt_activity.helpdesk_available_model_ids", False
        )
        if helpdesk_available_model_ids:
            res.update(
                helpdesk_available_model_ids=ast.literal_eval(
                    helpdesk_available_model_ids
                )
            )
        return res
