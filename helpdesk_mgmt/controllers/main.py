import logging

import werkzeug
from werkzeug.exceptions import BadRequest, Forbidden, NotFound

from odoo import http
from odoo.http import request
from odoo.tools import plaintext2html

_logger = logging.getLogger(__name__)


class HelpdeskTicketController(http.Controller):
    @http.route("/ticket/close", type="http", auth="user", methods=["POST"], csrf=True)
    def support_ticket_close(self, ticket_id=None, stage_id=None, **kw):
        """Close a visible ticket using one of its permitted closing stages."""
        try:
            ticket_id, stage_id = int(ticket_id), int(stage_id)
        except (TypeError, ValueError) as error:
            raise BadRequest() from error
        ticket = request.env["helpdesk.ticket"].search(
            [("id", "=", ticket_id)], limit=1
        )
        if not ticket:
            raise NotFound()
        stage = request.env["helpdesk.ticket.stage"].search(
            [("id", "=", stage_id)], limit=1
        )
        applicable_stages = (
            ticket.sudo()
            .team_id.with_company(ticket.company_id)
            ._get_applicable_stages()
        )
        if stage and stage.close_from_portal and stage in applicable_stages:
            ticket.sudo().stage_id = stage.id
        elif stage and not stage.close_from_portal:
            return werkzeug.utils.redirect(f"/my/ticket/{ticket.id}")
        else:
            raise Forbidden()
        return werkzeug.utils.redirect(f"/my/ticket/{ticket.id}")

    def _get_teams(self):
        return (
            http.request.env["helpdesk.ticket.team"]
            .with_company(request.env.company.id)
            .search([("active", "=", True), ("show_in_portal", "=", True)])
            if http.request.env.user.company_id.helpdesk_mgmt_portal_select_team
            else False
        )

    def _get_categories(self, **kw):
        company = request.env.company
        category_model = http.request.env["helpdesk.ticket.category"]
        domain = [("active", "=", True), ("show_in_portal", "=", True)]
        return (
            category_model.with_company(company.id).search(domain)
            if http.request.env.user.company_id.helpdesk_mgmt_portal_select_category
            else category_model
        )

    @http.route("/new/ticket", type="http", auth="user", website=True)
    def create_new_ticket(self, **kw):
        values = self._get_create_new_ticket_values(**kw)
        return http.request.render("helpdesk_mgmt.portal_create_ticket", values)

    def _get_create_new_ticket_values(self, **kw):
        session_info = http.request.env["ir.http"].session_info()
        company = request.env.company
        email = http.request.env.user.email
        name = http.request.env.user.name
        company = request.env.company
        return {
            "categories": self._get_categories(**kw),
            "teams": self._get_teams(),
            "email": email,
            "name": name,
            "ticket_team_id_required": (company.helpdesk_mgmt_portal_team_id_required),
            "ticket_category_id_required": (
                company.helpdesk_mgmt_portal_category_id_required
            ),
            "max_upload_size": session_info["max_file_upload_size"],
        }

    def _prepare_submit_ticket_vals(self, **kw):
        category = http.request.env["helpdesk.ticket.category"].browse(
            int(kw.get("category") or 0)
        )
        company = category.company_id or http.request.env.company
        vals = {
            "company_id": company.id,
            "category_id": category.id,
            "description": plaintext2html(kw.get("description")),
            "name": kw.get("subject"),
            "attachment_ids": False,
            "channel_id": request.env.ref(
                "helpdesk_mgmt.helpdesk_ticket_channel_web", False
            ).id,
            "partner_id": request.env.user.partner_id.id,
            "partner_name": request.env.user.partner_id.name,
            "partner_email": request.env.user.partner_id.email,
            "user_id": False,
        }
        team = http.request.env["helpdesk.ticket.team"]
        if company.helpdesk_mgmt_portal_select_team and kw.get("team"):
            team = (
                http.request.env["helpdesk.ticket.team"]
                .sudo()
                .search(
                    [("id", "=", int(kw.get("team"))), ("show_in_portal", "=", True)]
                )
            )
            vals["team_id"] = team.id
        # Need to set stage_id so that the _track_template() method is called
        # and the mail is sent automatically if applicable
        vals["stage_id"] = team._get_applicable_stages()[:1].id
        return vals

    @http.route(
        "/submitted/ticket",
        type="http",
        auth="user",
        website=True,
        methods=["POST"],
        csrf=True,
    )
    def submit_ticket(self, **kw):
        vals = self._prepare_submit_ticket_vals(**kw)
        new_ticket = request.env["helpdesk.ticket"].sudo().create(vals)
        new_ticket.message_subscribe(partner_ids=request.env.user.partner_id.ids)
        if kw.get("attachment"):
            for c_file in request.httprequest.files.getlist("attachment"):
                data = c_file.read()
                if c_file.filename:
                    request.env["ir.attachment"].sudo().create(
                        {
                            "name": c_file.filename,
                            "raw": data,
                            "res_model": "helpdesk.ticket",
                            "res_id": new_ticket.id,
                        }
                    )
        return werkzeug.utils.redirect(f"/my/ticket/{new_ticket.id}")
