# Copyright (C) 2024 Irlui Ramírez <iramirez.spain@gmail.com>
# Copyright (C) 2024 Consultores Hoteleros Integrales <www.aldahotels.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

import odoo.http as http
from odoo.http import request

from odoo.addons.helpdesk_mgmt.controllers.main import HelpdeskTicketController

_logger = logging.getLogger(__name__)


class CustomHelpdeskTicketController(HelpdeskTicketController):
    @http.route("/web/dataset/call_kw", type="json", auth="user")
    def onchange_company_id(self, company_id):
        hotels = (
            request.env["pms.property"]
            .sudo()
            .search(
                [
                    ("company_id", "=", company_id),
                    ("user_ids", "in", [request.env.user.id]),  # Filtra por usuario
                ]
            )
        )

        result = {
            "domain": {
                "hotel_id": hotels.ids,
            },
            "data": {
                "hotels": {hotel.id: {"name": hotel.name} for hotel in hotels},
            },
        }
        return result

    @http.route("/new/ticket", type="http", auth="user", website=True)
    def create_new_ticket(self, **kw):
        response = super().create_new_ticket(**kw)
        # Obtener el usuario actual
        user = request.env.user
        # Verificar si el usuario pertenece al grupo helpdesk_mgmt.group_helpdesk_user_team
        user_belongs_to_group = user.has_group(
            "helpdesk_mgmt.group_helpdesk_user_team"
            or "helpdesk_mgmt.group_helpdesk_manager"
        )
        # Obtener las compañías asignadas al usuario actual
        assigned_companies = user.company_ids
        company = request.env.company
        tag_model = http.request.env["helpdesk.ticket.tag"]
        tags = tag_model.with_company(company.id).search([("active", "=", True)])
        # Get hotels list
        hotel_model = http.request.env["pms.property"]
        hotels = hotel_model.sudo().search(
            [("user_ids", "in", [http.request.env.user.id])]
        )
        all_room_ids = [room_id for hotel in hotels for room_id in hotel.room_ids.ids]
        room_model = http.request.env["pms.room"]
        rooms = room_model.sudo().search([("id", "in", all_room_ids)])
        return response.qcontext.update(
            "helpdesk_mgmt.portal_create_ticket",
            {
                "user_belongs_to_group": user_belongs_to_group,
                "companies": assigned_companies,
                "hotels": hotels,
                "rooms": rooms,
                "tags": tags,
            },
        )

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
                "hotel_id": request.params.get("hotel_id"),
                "room_id": request.params.get("room_id"),
                "tag_ids": request.params.get("tag_ids"),
            }
        )
        return vals

    # @http.route("/helpdesk_mgmt_pms/objects", type="http", auth="user")
    # def list(self, **kw):
    #     return http.request.render(
    #         "helpdesk_mgmt_pms.listing",
    #         {
    #             "root": "/helpdesk_mgmt_pms",
    #             "objects": http.request.env["main"].search([]),
    #         },
    #     )

    # @http.route('/helpdesk_mgmt_pms/objects/<model("main"):obj>', auth="public")
    # def object(self, obj, **kw):
    #     return http.request.render("helpdesk_mgmt_pms.object", {"object": obj})
