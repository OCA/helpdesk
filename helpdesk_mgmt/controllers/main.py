import logging
from base64 import b64encode

import werkzeug

import odoo.http as http
from odoo import SUPERUSER_ID
from odoo.http import request

_logger = logging.getLogger(__name__)


class HelpdeskTicketController(http.Controller):
    @http.route("/ticket/close", type="http", auth="user")
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

        return werkzeug.utils.redirect("/my/ticket/" + str(ticket.id))

    @http.route("/new/ticket", type="http", auth="user", website=True)
    def create_new_ticket(self, **kw):
        categories = http.request.env["helpdesk.ticket.category"].search(
            [("active", "=", True)]
        )
        email = http.request.env.user.email
        name = http.request.env.user.name
        return http.request.render(
            "helpdesk_mgmt.portal_create_ticket",
            {"categories": categories, "email": email, "name": name},
        )

    @http.route("/submitted/ticket", type="http", auth="user", website=True, csrf=True)
    def submit_ticket(self, **kw):
        vals = {
            "partner_name": kw.get("name"),
            "company_id": http.request.env.user.company_id.id,
            "category_id": kw.get("category"),
            "partner_email": kw.get("email"),
            "description": kw.get("description"),
            "name": kw.get("subject"),
            "attachment_ids": False,
            "partner_id": request.env["res.partner"]
            .with_user(SUPERUSER_ID)
            .search([("name", "=", kw.get("name")), ("email", "=", kw.get("email"))])
            .id,
        }
        new_ticket = request.env["helpdesk.ticket"].with_user(SUPERUSER_ID).create(vals)
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


class HelpdeskTeamForm(http.Controller):
    @http.route("/helpdesk/<string:endpoint>", type="http", auth="user", website=True)
    def create_new_team_ticket(self, endpoint):
        team_id = self._team_exists(endpoint)
        r = False  # don't brake the flow ~~
        if team_id:
            email = http.request.env.user.email
            name = http.request.env.user.name
            r = http.request.render(
                "helpdesk_mgmt.portal_create_team_ticket",
                {"email": email, "name": name, "id_team": team_id.id},
            )

        return r

    @http.route(
        "/helpdesk/ticket/team/submit",
        type="http",
        auth="user",
        website=True,
        csrf=True,
    )
    def submit_new_team_ticket(self, **kw):
        values = {
            "partner_name": kw.get("name"),
            "company_id": http.request.env.user.company_id.id,
            "category_id": kw.get("category"),
            "partner_email": kw.get("email"),
            "description": kw.get("description"),
            "name": kw.get("subject"),
            "team_id": kw.get("id_team"),
            "attachment_ids": False,
            "partner_id": request.env["res.partner"]
            .with_user(SUPERUSER_ID)
            .search([("name", "=", kw.get("name")), ("email", "=", kw.get("email"))])
            .id,
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
    def _team_exists(endpoint: str):
        return request.env["helpdesk.ticket.team"].search(
            [("endpoint_webform", "=", endpoint), ("enable_webform", "=", True)]
        )
