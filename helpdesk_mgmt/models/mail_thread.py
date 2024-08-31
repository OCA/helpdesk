# Copyright 2024 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>

from odoo import models


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _message_track_post_template(self, changes):
        if (
            self._context.get("default_fetchmail_server_id")
            and self._name == "helpdesk.ticket"
        ):
            changes.append("stage_id")
        return super()._message_track_post_template(changes)
