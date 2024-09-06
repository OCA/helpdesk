# Author: Andrius Laukavičius. Copyright: JSC Boolit
# Copyright 2019 Coop IT Easy SCRLfs
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class MailMessage(models.Model):
    _inherit = "mail.message"

    @api.model
    def is_reopener_message(self, vals):
        if not vals.get("model") == "helpdesk.ticket":
            return False
        if vals.get("message_type") == "notification":
            return False
        return True

    @api.model
    def create(self, vals):
        if self.is_reopener_message(vals):
            ticket = self.env["helpdesk.ticket"].search(
                [("id", "=", vals.get("res_id"))]
            )
            if ticket:
                if ticket.stage_id.closed:
                    stage = self.env["helpdesk.ticket.stage"].search(
                        [], order="sequence", limit=1
                    )
                    ticket.stage_id = stage
        return super().create(vals)
