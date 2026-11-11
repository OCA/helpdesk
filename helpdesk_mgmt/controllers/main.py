import logging

import werkzeug
from werkzeug.exceptions import BadRequest, Forbidden, NotFound

from odoo import http
from odoo.http import request
from odoo.tools import plaintext2html

_logger = logging.getLogger(__name__)


class HelpdeskTicketController(http.Controller):
    @staticmethod
    def _parse_submitted_id(value):
        """Cast a submitted record id, rejecting a non-numeric one."""
        try:
            return int(value)
        except (TypeError, ValueError) as error:
            raise BadRequest() from error

    def _get_portal_choice(self, records, value):
        """Resolve a submitted id against the records the portal offers."""
        if not value:
            return records.browse()
        choice = records.browse(self._parse_submitted_id(value)) & records
        if not choice:
            raise Forbidden()
        return choice

    def _get_portal_closing_stages(self, ticket):
        """Stages the portal may move ``ticket`` into to close it."""
        return (
            ticket.sudo()
            .team_id.with_company(ticket.company_id)
            ._get_applicable_stages()
            .filtered("close_from_portal")
        )

    @http.route("/ticket/close", type="http", auth="user", methods=["POST"], csrf=True)
    def support_ticket_close(self, ticket_id=None, stage_id=None):
        """Close a visible, still open ticket using one of its permitted stages."""
        ticket_id = self._parse_submitted_id(ticket_id)
        stage_id = self._parse_submitted_id(stage_id)
        ticket = request.env["helpdesk.ticket"].search(
            [("id", "=", ticket_id)], limit=1
        )
        if not ticket:
            raise NotFound()
        ticket_page = werkzeug.utils.redirect(f"/my/ticket/{ticket.id}")
        if ticket.sudo().closed:
            return ticket_page
        if stage_id not in self._get_portal_closing_stages(ticket).ids:
            raise Forbidden()
        ticket.sudo().stage_id = stage_id
        return ticket_page

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
        category = self._get_portal_choice(
            self._get_categories(**kw), kw.get("category")
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
            team = self._get_portal_choice(
                self._get_teams() or request.env["helpdesk.ticket.team"],
                kw.get("team"),
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
