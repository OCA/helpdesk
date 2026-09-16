# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _skip_ticket_stage_update_from_autoreply(self, message, message_dict, routes):
        if self._message_route_process_autoreply(message, message_dict, routes):
            return True
        return super()._skip_ticket_stage_update_from_autoreply(
            message, message_dict, routes
        )
