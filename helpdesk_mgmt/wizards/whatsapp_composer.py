# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class WhatsappComposer(models.TransientModel):
    _inherit = "whatsapp.composer"

    def _action_send_whatsapp(self):
        super()._action_send_whatsapp()
        if self.res_model != "helpdesk.ticket" or not self.res_id:
            return
        ticket = self.env["helpdesk.ticket"].browse(self.res_id)
        # Mirror sent message into ticket chatter
        ticket.with_context(link_gateway_message=True).message_post(
            body=self.body or "",
            subtype_xmlid="mail.mt_comment",
            message_type="comment",
        )
        # Link channel to ticket so incoming replies route here
        channel = ticket._whatsapp_get_channel(self.number_field_name, self.gateway_id)
        if channel and not ticket.whatsapp_channel_id:
            ticket.whatsapp_channel_id = channel.id
