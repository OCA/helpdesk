# Copyright 2024 Antoni Marroig(APSL-Nagarro)<amarroig@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from werkzeug.exceptions import Forbidden

import odoo.http as http
from odoo.http import request
from odoo.osv import expression

from odoo.addons.mail.tools.discuss import Store

# _message_post_helper deprected in 18.0.
from odoo.addons.portal.controllers.mail import PortalChatter


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

    # portal_chatter_post method was removed in 18.0.
    @http.route("/mail/chatter_fetch", type="json", auth="public", website=True)
    def portal_message_fetch(
        self, thread_model, thread_id, limit=10, after=None, before=None, **kw
    ):
        # Only search into website_message_ids, so apply the same domain to perform
        # only one search extract domain from the 'website_message_ids' field
        model = request.env[thread_model]
        field = model._fields["website_message_ids"]
        domain = expression.AND(
            [
                self._setup_portal_message_fetch_extra_domain(kw),
                field.get_domain_list(model),
                [
                    ("res_id", "=", thread_id),
                    "|",
                    ("body", "!=", ""),
                    ("attachment_ids", "!=", False),
                    ("subtype_id", "=", request.env.ref("mail.mt_comment").id),
                ],
            ]
        )
        # Check access
        Message = request.env["mail.message"]
        if kw.get("token"):
            access_as_sudo = request.env[thread_model]._get_thread_with_access(
                thread_id, token=kw.get("token")
            )
            if not access_as_sudo:  # if token is not correct, raise Forbidden
                raise Forbidden()
            # Non-employee see only messages with not internal subtype
            # (aka, no internal logs)
            if not request.env.user._is_internal():
                domain = expression.AND([Message._get_search_domain_share(), domain])
            Message = request.env["mail.message"].sudo()
        res = Message._message_fetch(domain, None, before, after, None, limit)
        messages = res.pop("messages")
        post_values = {
            "res_model": thread_model,
            "res_id": thread_id,
            "message": messages,
            "send_after_commit": False,
            "attachment_ids": False,  # will be added afterward
        }

        self.change_status_ticket_from_portal(post_values)
        return {
            **res,
            "data": {"mail.message": messages.portal_message_format(options=kw)},
            "messages": Store.many_ids(messages),
        }
