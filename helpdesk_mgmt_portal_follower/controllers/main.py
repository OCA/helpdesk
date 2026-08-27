import odoo.http as http
from odoo.http import request

from odoo.addons.helpdesk_mgmt.controllers.main import HelpdeskTicketController


class HelpdeskTicketController(HelpdeskTicketController):
    @http.route("/submitted/ticket", type="http", auth="user", website=True, csrf=True)
    def submit_ticket(self, **kw):
        res = super().submit_ticket(**kw)
        ticket_id = res.location.split("/")[-1]
        new_ticket = request.env["helpdesk.ticket"].browse(int(ticket_id))
        if kw.get("followers"):
            emails = [
                email.strip()
                for email in kw.get("followers").split(",")
                if email.strip()
            ]
            partner_ids = []

            for email in emails:
                partner = request.env["res.partner"].search([("email", "=", email)])
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
