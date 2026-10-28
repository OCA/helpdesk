# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    # When the image is inserted into the description,
    # a warning appears indicating a lack of permissions.
    # This code block adds "helpdesk.ticket" to the allowed group,
    # preventing the warning from being triggered.
    @api.model
    def _can_bypass_rights_on_media_dialog(self, **attachment_data):
        if attachment_data.get("res_model") == "helpdesk.ticket":
            return True
        return super()._can_bypass_rights_on_media_dialog(**attachment_data)
