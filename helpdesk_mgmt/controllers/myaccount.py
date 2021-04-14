# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, http
from odoo.exceptions import AccessError
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class CustomerPortalHelpdesk(CustomerPortal):
    def _prepare_portal_layout_values(self):
        values = super()._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        ticket_count = request.env["helpdesk.ticket"].search_count(
            [("partner_id", "child_of", partner.id)]
        )
        values["ticket_count"] = ticket_count
        return values

    def _helpdesk_ticket_check_access(self, ticket_id):
        ticket = request.env["helpdesk.ticket"].browse([ticket_id])
        ticket_sudo = ticket.sudo()
        try:
            ticket.check_access_rights("read")
            ticket.check_access_rule("read")
        except AccessError:
            raise
        return ticket_sudo

    @http.route(
        ["/my/tickets", "/my/tickets/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_tickets(
        self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw
    ):
        values = self._prepare_portal_layout_values()
        HelpdesTicket = request.env["helpdesk.ticket"]
        domain = []

        searchbar_sortings = {
            "date": {"label": _("Newest"), "order": "create_date desc"},
            "name": {"label": _("Name"), "order": "name"},
            "stage": {"label": _("Stage"), "order": "stage_id"},
            "update": {
                "label": _("Last Stage Update"),
                "order": "last_stage_update desc",
            },
        }
        searchbar_filters = {"all": {"label": _("All"), "domain": []}}
        for stage in request.env["helpdesk.ticket.stage"].search([]):
            searchbar_filters.update(
                {
                    str(stage.id): {
                        "label": stage.name,
                        "domain": [("stage_id", "=", stage.id)],
                    }
                }
            )

        # default sort by order
        if not sortby:
            sortby = "date"
        order = searchbar_sortings[sortby]["order"]

        # default filter by value
        if not filterby:
            filterby = "all"
        domain += searchbar_filters[filterby]["domain"]

        # count for pager
        ticket_count = HelpdesTicket.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/tickets",
            url_args={},
            total=ticket_count,
            page=page,
            step=self._items_per_page,
        )
        # content according to pager and archive selected
        tickets = HelpdesTicket.search(
            domain, order=order, limit=self._items_per_page, offset=pager["offset"]
        )
        values.update(
            {
                "date": date_begin,
                "tickets": tickets,
                "page_name": "ticket",
                "pager": pager,
                "default_url": "/my/tickets",
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
                "searchbar_filters": searchbar_filters,
                "filterby": filterby,
            }
        )
        return request.render("helpdesk_mgmt.portal_my_tickets", values)

    @http.route(["/my/ticket/<int:ticket_id>"], type="http", website=True)
    def portal_my_ticket(self, ticket_id=None, **kw):
        try:
            ticket_sudo = self._helpdesk_ticket_check_access(ticket_id)
        except AccessError:
            return request.redirect("/my")
        values = self._ticket_get_page_view_values(ticket_sudo, **kw)
        return request.render("helpdesk_mgmt.portal_helpdesk_ticket_page", values)

    def _ticket_get_page_view_values(self, ticket, **kwargs):
        closed_stages = request.env["helpdesk.ticket.stage"].search(
            [("closed", "=", True)]
        )
        values = {
            "page_name": "ticket",
            "ticket": ticket,
            "closed_stages": closed_stages,
        }

        if kwargs.get("error"):
            values["error"] = kwargs["error"]
        if kwargs.get("warning"):
            values["warning"] = kwargs["warning"]
        if kwargs.get("success"):
            values["success"] = kwargs["success"]

        return values
