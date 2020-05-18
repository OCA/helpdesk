import logging
from base64 import b64encode

import werkzeug

import odoo.http as http
from odoo import SUPERUSER_ID
from odoo.http import request

_logger = logging.getLogger(__name__)


class HelpdeskTicketController(http.Controller):
    @http.route("/help", type="http", auth="public", website=True)
    def render_public_ticket(self):
        """
        :return: rendered template
        """

        user_email = None
        user_name = None
        user_id = None
        if not request.env.ref("base.public_user").id == request.env.user.id:
            user_email = http.request.env.user.email
            user_name = http.request.env.user.name
            user_id = http.request.env.user.id
        category_ids = (
            http.request.env["helpdesk.ticket.category"]
            .with_user(SUPERUSER_ID)
            .search([("active", "=", True)])
        )

        return http.request.render(
            "helpdesk_mgmt.portal_create_ticket",
            {
                "email": user_email,
                "name": user_name,
                "id_user": user_id,
                "categories": category_ids,
            },
        )

    @http.route("/help/ticket/submit", type="http", auth="public", website=True)
    def submit_ticket(self, **kw):
        """
         Main submit endpoint which receives calls from public and private rendering
        endpoints
        :param kw: values
        :return: a redirection to the thankyou endpoint
        """

        values = {
            "partner_name": kw.get("name"),
            "category_id": kw.get("category"),
            "partner_email": kw.get("email"),
            "description": kw.get("description"),
            "name": kw.get("subject"),
            "attachment_ids": False,
            "company_id": http.request.env.user.company_id.id,
            "channel_id": self._search_id_channel(),
            "partner_id": self._search_id_partner(kw),
        }

        id_team = kw.get("id_team")
        if id_team and str.isdigit(id_team):
            values.update({"team_id": int(id_team)})

        new_ticket = (
            request.env["helpdesk.ticket"].with_user(SUPERUSER_ID).create(values)
        )
        new_ticket.message_subscribe(partner_ids=request.env.user.partner_id.ids)

        if kw.get("attachment"):
            for c_file in request.httprequest.files.getlist("attachment"):
                data = c_file.read()
                if c_file.filename:
                    request.env["ir.attachment"].with_user(SUPERUSER_ID).create(
                        {
                            "name": c_file.filename,
                            "datas": b64encode(data),
                            "store_fname": c_file.filename,
                            "res_model": "helpdesk.ticket",
                            "res_id": new_ticket.id,
                        }
                    )
        return werkzeug.utils.redirect("/help/thankyou")

    @http.route("/help/ticket/close", type="http", auth="user")
    def support_ticket_close(self, **kw):
        """Close the support ticket"""
        values = {}
        for field_name, field_value in kw.items():
            if field_name.endswith("_id"):
                values[field_name] = int(field_value)
            else:
                values[field_name] = field_value
        ticket = (
            http.request.env["helpdesk.ticket"]
            .with_user(SUPERUSER_ID)
            .search([("id", "=", values["ticket_id"])])
        )
        ticket.stage_id = values.get("stage_id")

        return werkzeug.utils.redirect("/my/ticket/%s" % str(ticket.id))

    @http.route("/help/thankyou", type="http", auth="public", website=True, csrf=True)
    def thankyou_ticket(self):
        return http.request.render("helpdesk_mgmt.portal_thankyou_ticket")

    @http.route(
        "/help/team/<string:endpoint>", type="http", auth="public", website=True
    )
    def create_new_team_ticket(self, endpoint):
        user_email = None
        user_name = None
        user_id = None
        if not request.env.ref("base.public_user").id == request.env.user.id:
            user_email = http.request.env.user.email
            user_name = http.request.env.user.name
            user_id = http.request.env.user.id
        category_ids = (
            http.request.env["helpdesk.ticket.category"]
            .with_user(SUPERUSER_ID)
            .search([("active", "=", True)])
        )
        team_id = self._search_team_id(endpoint)
        r = False  # maybe some day someone'll make a cool error template
        if team_id:
            r = False
            if team_id.enable_public_webform or user_id:
                r = http.request.render(
                    "helpdesk_mgmt.portal_create_ticket",
                    {
                        "email": user_email,
                        "name": user_name,
                        "id_team": team_id.id,
                        "id_user": user_id,
                        "categories": category_ids,
                    },
                )
        return r

    @http.route(
        "/help/ticket/team/submit", type="http", auth="user", website=True, csrf=True,
    )
    def submit_new_team_ticket(self, **kw):
        values = {
            "partner_name": kw.get("name"),
            "company_id": http.request.env.user.company_id.id,
            "category_id": kw.get("category"),
            "partner_email": kw.get("email"),
            "description": kw.get("description"),
            "name": kw.get("subject"),
            "team_id": int(kw.get("id_team")),
            "attachment_ids": False,
            "partner_id": self._search_id_partner(kw),
            "channel_id": self._search_id_channel(),
        }
        new_ticket = (
            request.env["helpdesk.ticket"].with_user(SUPERUSER_ID).create(values)
        )
        new_ticket.message_subscribe(partner_ids=request.env.user.partner_id.ids)
        if kw.get("attachment"):
            for c_file in request.httprequest.files.getlist("attachment"):
                data = c_file.read()
                if c_file.filename:
                    request.env["ir.attachment"].with_user(SUPERUSER_ID).create(
                        {
                            "name": c_file.filename,
                            "datas": b64encode(data),
                            "store_fname": c_file.filename,
                            "res_model": "helpdesk.ticket",
                            "res_id": new_ticket.id,
                        }
                    )
        return werkzeug.utils.redirect("/my/tickets")

    @staticmethod
    def _search_id_partner(kw: dict) -> int:
        id_partner = kw.get("id_partner")
        if id_partner and str.isdigit(id_partner):
            id_partner = int(id_partner)
        else:
            partner_id = (
                request.env["res.partner"]
                .with_user(SUPERUSER_ID)
                .search([("email", "=", kw.get("email"))])
            )
            id_partner = partner_id[0].id if partner_id else None
        return id_partner

    @staticmethod
    def _search_id_channel() -> int:
        channel_id = (
            request.env["helpdesk.ticket.channel"]
            .with_user(SUPERUSER_ID)
            .search([("name", "=", "Web")])
        )
        return channel_id[0].id if channel_id else None

    def _search_id_team(self, endpoint: str) -> int:
        team_id = self._search_team_id(endpoint)
        return team_id[0].id if team_id else None

    @staticmethod
    def _search_team_id(endpoint: str):
        return (
            request.env["helpdesk.ticket.team"]
            .with_user(SUPERUSER_ID)
            .search(
                [("endpoint_webform", "=", endpoint), ("enable_webform", "=", True)]
            )
        )
