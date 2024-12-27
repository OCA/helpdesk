# Copyright 2024 Antoni Marroig(APSL-Nagarro)<amarroig@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import odoo.http as http
from odoo.http import request
from odoo.tools import plaintext2html

from odoo.addons.portal.controllers.mail import PortalChatter, _message_post_helper


class HelpdeskCustomerResponse(PortalChatter):
    def change_status_ticket_from_portal(self, post_values):
        if post_values["res_model"] == "helpdesk.ticket":
            ticket_id = post_values["res_id"]
            ticket = request.env["helpdesk.ticket"].sudo().browse(int(ticket_id))
            if (
                ticket
                and request.env.user.partner_id.id == ticket.partner_id.id
                and ticket.team_id.autoupdate_ticket_stage
                and ticket.stage_id in ticket.team_id.autopupdate_src_stage_ids
            ):
                ticket.stage_id = ticket.team_id.autopupdate_dest_stage_id.id

    @http.route(
        ["/mail/chatter_post"],
        type="json",
        methods=["POST"],
        auth="public",
        website=True,
    )
    def portal_chatter_post(
        self,
        res_model,
        res_id,
        message,
        attachment_ids=None,
        attachment_tokens=None,
        **kw
    ):
        if not self._portal_post_has_content(
            res_model,
            res_id,
            message,
            attachment_ids=attachment_ids,
            attachment_tokens=attachment_tokens,
            **kw
        ):
            return

        res_id = int(res_id)

        self._portal_post_check_attachments(
            attachment_ids or [], attachment_tokens or []
        )

        result = {"default_message": message}
        # message is received in plaintext and saved in html
        if message:
            message = plaintext2html(message)
        post_values = {
            "res_model": res_model,
            "res_id": res_id,
            "message": message,
            "send_after_commit": False,
            "attachment_ids": False,  # will be added afterward
        }
        post_values.update(
            (fname, kw.get(fname)) for fname in self._portal_post_filter_params()
        )
        post_values["_hash"] = kw.get("hash")
        message = _message_post_helper(**post_values)
        result.update({"default_message_id": message.id})

        if attachment_ids:
            # sudo write the attachment to bypass the read access
            # verification in mail message
            record = request.env[res_model].browse(res_id)
            message_values = {"res_id": res_id, "model": res_model}
            attachments = record._message_post_process_attachments(
                [], attachment_ids, message_values
            )

            if attachments.get("attachment_ids"):
                message.sudo().write(attachments)

            result.update(
                {
                    "default_attachment_ids": message.attachment_ids.sudo().read(
                        ["id", "name", "mimetype", "file_size", "access_token"]
                    )
                }
            )

        self.change_status_ticket_from_portal(post_values)
        return result
