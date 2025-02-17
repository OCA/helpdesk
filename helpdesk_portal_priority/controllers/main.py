import logging

import odoo.http as http

from odoo.addons.helpdesk_mgmt.controllers.main import HelpdeskTicketController

_logger = logging.getLogger(__name__)


class HelpdeskPriorityController(HelpdeskTicketController):
    @http.route("/new/ticket", type="http", auth="user", website=True)
    def create_new_ticket(self, **kw):
        res = super().create_new_ticket(**kw)
        priorities = (
            http.request.env["helpdesk.ticket"]
            ._fields["priority"]
            ._description_selection(http.request.env)
        )
        res.qcontext["priorities"] = priorities
        return res

    def _prepare_submit_ticket_vals(self, **kw):
        vals = super()._prepare_submit_ticket_vals(**kw)
        vals["priority"] = kw.get("priority")

        return vals
