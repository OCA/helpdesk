# Author: Andrius Laukavičius. Copyright: JSC Boolit
# Copyright 2019 Coop IT Easy SCRLfs
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, api


class MailMessage(models.Model):
    _inherit = "mail.message"

    def is_production_env(self):
        """ Used to determine how we will treat comments.
        It is useful because we can't (easily) mock
        incoming emails in testing environnements
        It needs to be implemented"""
        return False

    @api.model
    def is_reopener_message(self, vals):
        if not vals.get("model") == "helpdesk.ticket":
            return False
        if vals.get("message_type") == "notification":
            return False
        # We need to use comments in non-prod env for testing purposes
        if self.is_production_env() and vals.get("message_type") == "comment":
            return False
        return True

    @api.model
    def create(self, vals):
        if self.is_reopener_message(vals):
            ticket = self.env["helpdesk.ticket"].search(
                [("id", "=", vals.get("res_id"))]
            )
            if ticket:
                if ticket.stage_id.is_close:
                    stage = ticket.team_id.mapped("stage_ids").sorted(
                        "sequence"
                    )[0]
                    ticket.stage_id = stage
        return super(MailMessage, self).create(vals)
