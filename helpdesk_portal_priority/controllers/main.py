import logging

import odoo.http as http

from odoo.addons.helpdesk_mgmt.controllers.main import HelpdeskTicketController

_logger = logging.getLogger(__name__)


class HelpdeskPriorityController(HelpdeskTicketController):
    def _get_create_new_ticket_values(self, **kw):
        values = super()._get_create_new_ticket_values(**kw)
        values["priorities"] = (
            http.request.env["helpdesk.ticket"]
            ._fields["priority"]
            ._description_selection(http.request.env)
        )
        return values

    def _prepare_submit_ticket_vals(self, **kw):
        vals = super()._prepare_submit_ticket_vals(**kw)
        vals["priority"] = kw.get("priority")

        return vals
