# Copyright 2025 Marcel Savegnago - Escodoo <https://escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models


class ChatbotScriptStep(models.Model):
    _inherit = "chatbot.script.step"

    step_type = fields.Selection(
        selection_add=[("create_ticket", "Create Ticket")],
        ondelete={"create_ticket": "cascade"},
    )
    helpdesk_team_id = fields.Many2one(
        "helpdesk.ticket.team",
        string="Helpdesk Team",
        ondelete="set null",
        help="Used in combination with 'create_ticket' step type in order to automatically "
        "assign the created ticket to the defined team",
    )

    def _chatbot_helpdesk_prepare_ticket_values(self, mail_channel, description):
        return {
            "description": description + mail_channel._get_channel_history(),
            "name": _("%s's New Ticket", self.chatbot_script_id.title),
            "team_id": self.helpdesk_team_id.id,
            "user_id": False,
        }

    def _process_step(self, mail_channel):
        self.ensure_one()

        posted_message = super()._process_step(mail_channel)

        if self.step_type == "create_ticket":
            self._process_step_create_ticket(mail_channel)

        return posted_message

    def _process_step_create_ticket(self, mail_channel):
        """When reaching a 'create_ticket' step, we extract the relevant information:
        visitor's email, phone and conversation history to create a helpdesk.ticket.

        We use the email and phone to update the environment partner's information
        (if not a public user) if they differ from the current values.

        The whole conversation history will be saved into the ticket's description
        for reference. This also allows having a question of type 'free_input_multi'
        to let the visitor explain their issue / needs before creating the ticket."""

        customer_values = self._chatbot_prepare_customer_values(
            mail_channel, create_partner=False, update_partner=True
        )
        if self.env.user._is_public():
            create_values = {
                "partner_email": customer_values["email"],
                "partner_name": customer_values.get("name", ""),
            }
        else:
            partner = self.env.user.partner_id
            create_values = {
                "partner_id": partner.id,
                "company_id": partner.company_id.id,
            }

        create_values.update(
            self._chatbot_helpdesk_prepare_ticket_values(
                mail_channel, customer_values["description"]
            )
        )

        # Search for Livechat channel for the ticket
        livechat_channel = self.env.ref(
            "helpdesk_mgmt_livechat.helpdesk_ticket_channel_livechat",
            raise_if_not_found=False,
        )
        if livechat_channel:
            create_values["channel_id"] = livechat_channel.id
        else:
            # Fallback: search or create the channel if the reference doesn't exist
            livechat_channel = self.env["helpdesk.ticket.channel"].search(
                [("name", "=", "Livechat")], limit=1
            )
            if not livechat_channel:
                livechat_channel = self.env["helpdesk.ticket.channel"].create(
                    {"name": "Livechat"}
                )
            create_values["channel_id"] = livechat_channel.id

        self.env["helpdesk.ticket"].create(create_values)
