import logging

import odoo.http as http

from odoo.addons.helpdesk_mgmt.controllers.main import HelpdeskTicketController

_logger = logging.getLogger(__name__)


class HelpdeskPartnerTeamCategoryController(HelpdeskTicketController):
    def _get_teams(self):
        teams = super()._get_teams()
        partner = http.request.env.user.partner_id
        if partner.helpdesk_team_ids:
            teams = teams.filtered(lambda x: x in partner.helpdesk_team_ids)
        return teams

    def _get_categories(self, **kw):
        categories = super()._get_categories(**kw)
        partner = http.request.env.user.partner_id
        if partner.helpdesk_category_ids:
            categories = categories.filtered(
                lambda x: x in partner.helpdesk_category_ids
            )
        return categories
