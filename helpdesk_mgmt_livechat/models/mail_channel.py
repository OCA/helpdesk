# Copyright 2025 Marcel Savegnago - Escodoo <https://escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, models
from odoo.tools import html2plaintext


class DiscussChannel(models.Model):
    _inherit = "discuss.channel"

    def execute_command_ticket(self, **kwargs):
        partner = self.env.user.partner_id
        key = kwargs["body"]
        if key.strip() == "/ticket":
            msg = _("Create a new ticket (/ticket ticket title)")
        else:
            ticket = self._convert_visitor_to_ticket(partner, key)
            msg = _(
                "Created a new ticket: %s",
                ticket._get_html_link(),
            )
        self.env.user._bus_send_transient_message(self, msg)

    def _convert_visitor_to_ticket(self, partner, key):
        """Create a ticket from channel /ticket command
        :param partner: internal user partner (operator) that created the ticket;
        :param key: operator input in chat ('/ticket Ticket about Issue')
        """
        # if public user is part of the chat: consider ticket to be linked to an
        # anonymous user whatever the participants. Otherwise keep only share
        # partners (no user or portal user) to link to the ticket.
        customers = self.env["res.partner"]
        for customer in self.with_context(
            active_test=False
        ).channel_partner_ids.filtered(lambda p: p != partner and p.partner_share):
            if customer.is_public:
                customers = self.env["res.partner"]
                break
            else:
                customers |= customer

        # Search for Livechat channel for the ticket
        livechat_channel = self.env.ref(
            "helpdesk_mgmt_livechat.helpdesk_ticket_channel_livechat",
            raise_if_not_found=False,
        )
        if not livechat_channel:
            # Fallback: search or create the channel if the reference doesn't exist
            livechat_channel = self.env["helpdesk.ticket.channel"].search(
                [("name", "=", "Livechat")], limit=1
            )
            if not livechat_channel:
                livechat_channel = self.env["helpdesk.ticket.channel"].create(
                    {"name": "Livechat"}
                )

        return self.env["helpdesk.ticket"].create(
            {
                "name": html2plaintext(key[7:]),  # Remove '/ticket ' from the beginning
                "partner_id": customers[0].id if customers else False,
                "user_id": False,
                "team_id": False,
                "description": self._get_channel_history(),
                "channel_id": livechat_channel.id,
            }
        )
