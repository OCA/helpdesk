# Copyright 2025 Onestein - Anjeel Haria
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    def _message_post_after_hook(self, message, msg_vals):
        """Change status of ticket if the required conditions are satisfied"""
        public_user = self.env.ref("base.public_user")
        if (
            self
            and self.env.user.partner_id.id
            in (self.partner_id.id, public_user.partner_id.id)
            and self.team_id.autoupdate_ticket_stage
            and self.stage_id in self.team_id.autopupdate_src_stage_ids
        ):
            self.sudo().stage_id = self.team_id.autopupdate_dest_stage_id.id
        return super()._message_post_after_hook(message, msg_vals)
