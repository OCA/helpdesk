# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class MailGatewayWhatsapp(models.AbstractModel):
    _inherit = "mail.gateway.whatsapp"

    def _post_process_message(self, message, channel):
        super()._post_process_message(message, channel)
        ticket = self._get_or_create_helpdesk_ticket(channel)
        if not ticket or not (message.body or message.attachment_ids):
            return
        ticket_msg = ticket.with_context(
            link_gateway_message=True
        ).message_post(
            body=message.body or "",
            author_id=message.author_id.id if message.author_id else False,
            gateway_type="whatsapp",
            date=message.date,
            subtype_xmlid="mail.mt_comment",
            message_type="comment",
            attachment_ids=message.attachment_ids.ids,
        )
        message.gateway_message_id = ticket_msg

    def _get_or_create_helpdesk_ticket(self, channel):
        # Already linked to a ticket?
        ticket = self.env["helpdesk.ticket"].search(
            [("whatsapp_channel_id", "=", channel.id)], limit=1
        )
        if ticket:
            return ticket

        # Identify the customer partner from channel members
        partner = channel.channel_member_ids.partner_id.filtered(
            lambda p: not p.user_ids or all(u.share for u in p.user_ids)
        )[:1]
        if not partner:
            partner = channel.channel_member_ids.partner_id[:1]

        # Reuse the most recent open ticket for this partner (without a WA channel)
        if partner:
            ticket = self.env["helpdesk.ticket"].search(
                [
                    ("partner_id", "=", partner.id),
                    ("closed", "=", False),
                    ("whatsapp_channel_id", "=", False),
                ],
                order="create_date desc",
                limit=1,
            )

        if not ticket:
            team = self.env["helpdesk.ticket.team"].search([], limit=1)
            vals = {
                "name": f"WhatsApp: {channel.name or 'Unknown'}",
                "description": "<p>Ticket created from incoming WhatsApp message.</p>",
            }
            if partner:
                vals.update(
                    {
                        "partner_id": partner.id,
                        "partner_name": partner.name,
                        "partner_email": partner.email or "",
                    }
                )
            if team:
                vals["team_id"] = team.id
            ticket = self.env["helpdesk.ticket"].sudo().create(vals)

        ticket.sudo().whatsapp_channel_id = channel.id
        return ticket
