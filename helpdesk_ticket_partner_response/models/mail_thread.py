from odoo import api, models
from odoo.tools import email_normalize


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    @api.model
    def _message_route_process(self, message, message_dict, routes):
        if not self._skip_ticket_stage_update_from_autoreply(
            message, message_dict, routes
        ):
            self.change_ticket_status_via_mail(routes, message_dict)
        return super()._message_route_process(message, message_dict, routes)

    def _skip_ticket_stage_update_from_autoreply(self, message, message_dict, routes):
        """Return True to suppress stage updates triggered by auto-reply emails.

        Override in integration modules to implement auto-reply detection.
        Returns False by default so no update is suppressed.
        """
        return False

    def change_ticket_status_via_mail(self, routes, message_dict):
        if routes and routes[0][0] == "helpdesk.ticket":
            ticket_id = routes[0][1]
            if not ticket_id:
                return None
            email_from = message_dict.get("email_from")
            if email_from:
                email_from = email_normalize(email_from)

            ticket = self.env["helpdesk.ticket"].sudo().browse(int(ticket_id)).exists()
            user_id = routes[0][3]
            if ticket:
                if not (
                    ticket.team_id.autoupdate_ticket_stage
                    and ticket.stage_id in ticket.team_id.autopupdate_src_stage_ids
                ):
                    return None

                email_partner = False
                ticket_partner = ticket.partner_id

                if user_id:
                    email_partner = (
                        self.env["res.users"]
                        .search([("id", "=", user_id)], limit=1)
                        .partner_id
                    )

                if email_partner and ticket_partner:
                    # Both known: compare by partner ID (most reliable)
                    update_stage = email_partner.id == ticket_partner.id
                elif email_partner:
                    # Known user sender, no ticket partner: compare normalized emails
                    update_stage = email_normalize(
                        email_partner.email
                    ) == email_normalize(ticket.partner_email)
                elif ticket_partner:
                    # No matching user sender, ticket has partner: compare emails
                    update_stage = email_normalize(ticket_partner.email) == email_from
                else:
                    # No linked partners on either side: compare normalized emails
                    update_stage = email_normalize(ticket.partner_email) == email_from

                if update_stage:
                    ticket.stage_id = ticket.team_id.autopupdate_dest_stage_id.id

        return None
