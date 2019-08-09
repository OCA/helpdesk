import logging
import werkzeug
import odoo.http as http
_logger = logging.getLogger(__name__)


class HelpdeskTicketController(http.Controller):

    @http.route('/ticket/close', type="http", auth="user")
    def support_ticket_close(self, **kw):
        """Close the support ticket"""
        values = {}
        for field_name, field_value in kw.items():
            if field_name.endswith('_id'):
                values[field_name] = int(field_value)
            else:
                values[field_name] = field_value
        ticket = http.request.env['helpdesk.ticket'].sudo().browse([(
            'id', '=', values['ticket_id'])])
        stage_id = int(values.get('stage_id'))
        ticket.update({'stage_id': stage_id})
        return werkzeug.utils.redirect("/my/ticket/" + str(ticket.id))
