# Copyright 2026 Paloma González-Ripoll(APSL-Nagarro)<paloma.gonzalez@nagarro.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    @api.model
    def _message_route_process(self, message, message_dict, routes):
        allowed_routes = []
        for route in routes or ():
            model, thread_id, custom_values, user_id, alias = route
            if (
                model == "helpdesk.ticket"
                and not thread_id
                and self._is_ticket_creation_blocked(message_dict)
            ):
                continue
            allowed_routes.append(route)
        return super()._message_route_process(message, message_dict, allowed_routes)

    def _is_ticket_creation_blocked(self, message_dict):
        partner_id = message_dict.get("author_id")
        partner = (
            self.env["res.partner"].browse(partner_id)
            if partner_id
            else self.env["res.partner"]
        )
        if not partner.block_ticket_creation:
            return False
        self.env.ref(
            "helpdesk_ticket_partner_block.mail_template_ticket_creation_blocked"
        ).send_mail(partner.id, force_send=True)
        return True
