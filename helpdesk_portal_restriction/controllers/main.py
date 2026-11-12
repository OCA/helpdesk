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

    def _get_category(self):
        return (
            http.request.env.user.partner_id.helpdesk_category_ids
            if http.request.env.user.partner_id.helpdesk_category_ids
            else http.request.env["helpdesk.ticket.category"].search(
                [("active", "=", True)]
            )
        )

    @http.route("/new/ticket", type="http", auth="user", website=True)
    def create_new_ticket(self, **kw):
        session_info = http.request.env["ir.http"].session_info()
        email = http.request.env.user.email
        name = http.request.env.user.name
        company = request.env.company
        return http.request.render(
            "helpdesk_mgmt.portal_create_ticket",
            {
                "categories": self._get_category(),
                "teams": self._get_teams(),
                "email": email,
                "name": name,
                "ticket_team_id_required": (
                    company.helpdesk_mgmt_portal_team_id_required
                ),
                "ticket_category_id_required": (
                    company.helpdesk_mgmt_portal_category_id_required
                ),
                "max_upload_size": session_info["max_file_upload_size"],
            },
        )
