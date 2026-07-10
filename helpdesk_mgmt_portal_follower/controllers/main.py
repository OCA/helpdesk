import re

import odoo.http as http
from odoo.http import request

from odoo.addons.helpdesk_mgmt.controllers.main import HelpdeskTicketController


class HelpdeskTicketController(HelpdeskTicketController):
    @http.route("/submitted/ticket", type="http", auth="user", website=True, csrf=True)
    def submit_ticket(self, **kw):
        res = super().submit_ticket(**kw)

        ticket_id = res.location.split("/")[-1]
        new_ticket = request.env["helpdesk.ticket"].browse(int(ticket_id))

        follower_emails = self._parse_follower_emails(kw.get("followers", ""))

        partner_ids = []

        for email in follower_emails:
            partner = (
                request.env["res.partner"]
                .sudo()
                .search(
                    [("email", "=ilike", email)],
                    limit=1,
                )
            )
            if not partner:
                reg = {
                    "name": email,
                    "email": email,
                    "type": "contact",
                }
                partner = request.env["res.partner"].sudo().create(reg)

            partner_ids.append(partner.id)

        new_ticket.sudo().message_subscribe(partner_ids=partner_ids)

        return res

    @staticmethod
    def _parse_follower_emails(emails):
        return list(
            {
                email.strip().lower()
                for email in re.split(r"[\s,;]+", emails)
                if email.strip()
            }
        )
