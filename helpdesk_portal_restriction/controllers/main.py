import logging

import odoo.http as http
from odoo.http import request

from odoo.addons.helpdesk_mgmt.controllers.main import HelpdeskTicketController

_logger = logging.getLogger(__name__)


class HelpdeskPartnerTeamCategoryController(HelpdeskTicketController):
    def _get_teams(self):
        if http.request.env.user.company_id.helpdesk_mgmt_portal_select_team:
            return (
                http.request.env.user.partner_id.helpdesk_team_ids
                if http.request.env.user.partner_id.helpdesk_team_ids
                else http.request.env["helpdesk.ticket.team"]
                .sudo()
                .search([("active", "=", True), ("show_in_portal", "=", True)])
            )
        else:
            return False

    def _get_categories(self, **kw):
        return (
            http.request.env.user.partner_id.helpdesk_category_ids
            if http.request.env.user.partner_id.helpdesk_category_ids
            else http.request.env["helpdesk.ticket.category"].search(
                [("active", "=", True)]
            )
        )
