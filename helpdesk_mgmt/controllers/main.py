import werkzeug
import logging
import odoo.http as http
_logger = logging.getLogger(__name__)


class HelpdeskTicketController(http.Controller):

    @http.route('/ticket/close', type="http", auth="user")
    def support_ticket_close(self, **kw):
        """Close the support ticket"""
        values = {}
        for field_name, field_value in kw.items():
            values[field_name] = field_value
        ticket = http.request.env['helpdesk.ticket'].sudo().\
            search([('id', '=', values['ticket_id'])])
        ticket.stage_id = values.get('stage_id')

        return werkzeug.utils.redirect("/my/ticket/" + str(ticket.id))
