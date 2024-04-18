# Copyright 2024 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    @classmethod
    def _get_translation_frontend_modules_name(cls):
        mods = super(IrHttp, cls)._get_translation_frontend_modules_name()
        return mods + ["helpdesk_mgmt"]
