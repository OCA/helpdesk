# Copyright (C) 2024 Irlui Ramírez <iramirez.spain@gmail.com>
# Copyright (C) 2024 Consultores Hoteleros Integrales <www.aldahotels.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

import odoo.http as http
from odoo.http import request

from odoo.addons.helpdesk_mgmt.controllers.main import HelpdeskTicketController

_logger = logging.getLogger(__name__)


class CustomHelpdeskTicketController(HelpdeskTicketController):
    @http.route("/new/ticket", type="http", auth="user", website=True)
    def create_new_ticket(self, **kw):
        response = super().create_new_ticket(**kw)
        user = request.env.user
        user_belongs_to_group = user.has_group(
            "helpdesk_mgmt.group_helpdesk_user_team"
            or "helpdesk_mgmt.group_helpdesk_manager"
        )
        assigned_companies = user.company_ids
        company = request.env.company
        tag_model = http.request.env["helpdesk.ticket.tag"]
        tags = tag_model.with_company(company.id).search([("active", "=", True)])
        property_model = http.request.env["pms.property"]
        propertys = property_model.sudo().search(
            [("user_ids", "in", [http.request.env.user.id])]
        )
        all_room_ids = [
            room_id for property in propertys for room_id in property.room_ids.ids
        ]
        room_model = http.request.env["pms.room"]
        rooms = room_model.sudo().search([("id", "in", all_room_ids)])
        response.qcontext.update(
            {
                "user_belongs_to_group": user_belongs_to_group,
                "companies": assigned_companies,
                "propertys": propertys,
                "rooms": rooms,
                "tags": tags,
            }
        )
        return response

    def _prepare_submit_ticket_vals(self, **kw):
        vals = super()._prepare_submit_ticket_vals(**kw)
        selected_company = kw.get("company_id")
        if selected_company is None:
            company = http.request.env.user.company_id
        else:
            company = (
                http.request.env["res.company"].sudo().browse(int(selected_company))
            )
        vals.update(
            {
                "company_id": company.id,
                "property_id": request.params.get("property_id"),
                "room_id": request.params.get("room_id"),
                "tag_ids": request.params.get("tag_ids"),
            }
        )
        return vals
