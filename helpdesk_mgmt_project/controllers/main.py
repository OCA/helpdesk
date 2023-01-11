# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

import odoo.http as http

from odoo.addons.helpdesk_mgmt.controllers.main import HelpdeskTicketController

_logger = logging.getLogger(__name__)


class CustomHelpdeskTicketController(HelpdeskTicketController):
    def _prepare_submit_ticket_vals(self, **kw):
        vals = super(CustomHelpdeskTicketController, self)._prepare_submit_ticket_vals(
            **kw
        )
        team = (
            http.request.env["helpdesk.ticket.team"].sudo().browse(vals.get("team_id"))
        )
        if team.default_project_id and not vals.get("project_id"):
            vals["project_id"] = team.default_project_id.id
        return vals
