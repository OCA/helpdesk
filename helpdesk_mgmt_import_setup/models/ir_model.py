# Copyright 2025 Kencove (https://www.kencove.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, models


class IrModelData(models.Model):
    _inherit = "ir.model.data"

    @api.model
    def _module_data_uninstall(self, modules_to_remove):
        if self.env.context.get("skip_remove_mail_message_and_followers"):
            self = self.with_context(skip_remove_mail_message_and_followers=True)
        return super(IrModelData, self)._module_data_uninstall(
            modules_to_remove=modules_to_remove
        )
