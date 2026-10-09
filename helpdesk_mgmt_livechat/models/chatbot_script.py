# Copyright 2025 Marcel Savegnago - Escodoo <https://escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ChatbotScript(models.Model):
    _inherit = "chatbot.script"

    ticket_count = fields.Integer(
        string="Generated Ticket Count", compute="_compute_ticket_count"
    )

    def _compute_ticket_count(self):
        if self.ids:
            # Search for all tickets created via livechat
            # We use the chatbot title in the description to identify related tickets
            for script in self:
                tickets = (
                    self.env["helpdesk.ticket"]
                    .with_context(active_test=False)
                    .sudo()
                    .search_count(
                        [
                            ("description", "ilike", script.title),
                            ("channel_id.name", "=", "Livechat"),
                        ]
                    )
                )
                script.ticket_count = tickets

    def action_view_tickets(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "helpdesk_mgmt.helpdesk_ticket_action"
        )
        # Filter tickets created via livechat related to this chatbot
        action["domain"] = [
            ("description", "ilike", self.title),
            ("channel_id.name", "=", "Livechat"),
        ]
        action["context"] = {"create": False}
        return action
