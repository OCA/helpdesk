from odoo import api, models


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    @api.model
    def _message_route_process(self, message, message_dict, routes):
        self.change_status_ticket_from_portal(routes, message_dict)
        return super()._message_route_process(message, message_dict, routes)

    def change_status_ticket_from_portal(self, routes, message_dict=None):
        if routes and routes[0][0] == "helpdesk.ticket":
            ticket_id = routes[0][1]
            # When the email creates the ticket/thread, Odoo can route the message
            # with a missing (None) id. In that case we must not crash.
            if ticket_id is None:
                return
            try:
                ticket_id_int = int(ticket_id)
            except (TypeError, ValueError):
                return

            ticket = self.env["helpdesk.ticket"].sudo().browse(ticket_id_int)
            author_id = message_dict and message_dict.get("author_id")
            if (
                ticket.exists()
                and author_id == ticket.partner_id.id
                and ticket.team_id.autoupdate_ticket_stage
                and ticket.stage_id in ticket.team_id.autopupdate_src_stage_ids
            ):
                ticket.stage_id = ticket.team_id.autopupdate_dest_stage_id.id
