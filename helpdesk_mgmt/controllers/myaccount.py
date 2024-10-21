# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from collections import OrderedDict
from operator import itemgetter

from odoo import _, http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.osv.expression import AND, OR
from odoo.tools import groupby as groupbyelem

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class CustomerPortalHelpdesk(CustomerPortal):
    """Routes called in portal mode to manage tickets.
    Very similar to those in the "project" module defined to manage tasks.
    """

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "ticket_count" in counters:
            helpdesk_model = request.env["helpdesk.ticket"]
            ticket_count = (
                helpdesk_model.search_count([])
                if helpdesk_model.check_access_rights("read", raise_exception=False)
                else 0
            )
            values["ticket_count"] = ticket_count
        return values

    @http.route(
        ["/my/tickets", "/my/tickets/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_tickets(
        self,
        page=1,
        date_begin=None,
        date_end=None,
        sortby=None,
        filterby=None,
        search=None,
        search_in=None,
        groupby=None,
        **kw
    ):
        HelpdeskTicket = request.env["helpdesk.ticket"]
        # Avoid error if the user does not have access.
        if not HelpdeskTicket.check_access_rights("read", raise_exception=False):
            return request.redirect("/my")

        values = self._prepare_portal_layout_values()

        searchbar_sortings = self._ticket_get_searchbar_sortings()
        searchbar_sortings = dict(
            sorted(
                self._ticket_get_searchbar_sortings().items(),
                key=lambda item: item[1]["sequence"],
            )
        )

        searchbar_filters = {
            "all": {"label": _("All"), "domain": []},
        }
        for stage in request.env["helpdesk.ticket.stage"].search([]):
            searchbar_filters[str(stage.id)] = {
                "label": stage.name,
                "domain": [("stage_id", "=", stage.id)],
            }

        searchbar_inputs = self._ticket_get_searchbar_inputs()
        searchbar_groupby = self._ticket_get_searchbar_groupby()

        if not sortby:
            sortby = "date"
        order = searchbar_sortings[sortby]["order"]

        if not filterby:
            filterby = "all"
        domain = searchbar_filters.get(filterby, searchbar_filters.get("all"))["domain"]

        if not groupby:
            groupby = "none"

        if date_begin and date_end:
            domain += [
                ("create_date", ">", date_begin),
                ("create_date", "<=", date_end),
            ]

        if not search_in:
            search_in = "all"
        if search:
            domain += self._ticket_get_search_domain(search_in, search)

        domain = AND(
            [
                domain,
                request.env["ir.rule"]._compute_domain(HelpdeskTicket._name, "read"),
            ]
        )

        # count for pager
        ticket_count = HelpdeskTicket.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/tickets",
            url_args={
                "date_begin": date_begin,
                "date_end": date_end,
                "sortby": sortby,
                "filterby": filterby,
                "groupby": groupby,
                "search": search,
                "search_in": search_in,
            },
            total=ticket_count,
            page=page,
            step=self._items_per_page,
        )

        order = self._ticket_get_order(order, groupby)
        tickets = HelpdeskTicket.search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager["offset"],
        )
        request.session["my_tickets_history"] = tickets.ids[:100]

        groupby_mapping = self._ticket_get_groupby_mapping()
        group = groupby_mapping.get(groupby)
        if group:
            grouped_tickets = [
                request.env["helpdesk.ticket"].concat(*g)
                for k, g in groupbyelem(tickets, itemgetter(group))
            ]
        elif tickets:
            grouped_tickets = [tickets]
        else:
            grouped_tickets = []

        values.update(
            {
                "date": date_begin,
                "date_end": date_end,
                "grouped_tickets": grouped_tickets,
                "page_name": "ticket",
                "default_url": "/my/tickets",
                "pager": pager,
                "searchbar_sortings": searchbar_sortings,
                "searchbar_groupby": searchbar_groupby,
                "searchbar_inputs": searchbar_inputs,
                "search_in": search_in,
                "search": search,
                "sortby": sortby,
                "groupby": groupby,
                "searchbar_filters": OrderedDict(sorted(searchbar_filters.items())),
                "filterby": filterby,
            }
        )
        return request.render("helpdesk_mgmt.portal_my_tickets", values)

    @http.route(
        ["/my/ticket/<int:ticket_id>"], type="http", auth="public", website=True
    )
    def portal_my_ticket(self, ticket_id, access_token=None, **kw):
        try:
            ticket_sudo = self._document_check_access(
                "helpdesk.ticket", ticket_id, access_token=access_token
            )
        except (AccessError, MissingError):
            return request.redirect("/my")

        # ensure attachments are accessible with access token inside template
        for attachment in ticket_sudo.attachment_ids:
            attachment.generate_access_token()
        values = self._ticket_get_page_view_values(ticket_sudo, access_token, **kw)
        return request.render("helpdesk_mgmt.portal_helpdesk_ticket_page", values)

    def _ticket_get_page_view_values(self, ticket, access_token, **kwargs):
        closed_stages = ticket.team_id._get_applicable_stages().filtered(
            lambda s: s.close_from_portal
        )
        files = (
            request.env["ir.attachment"]
            .sudo()
            .search(
                [
                    ("res_model", "=", "helpdesk.ticket"),
                    ("res_id", "=", ticket.id),
                ]
            )
        )
        values = {
            "closed_stages": closed_stages,  # used to display close buttons
            "page_name": "ticket",
            "ticket": ticket,
            "user": request.env.user,
            "files": files,
        }
        return self._get_page_view_values(
            ticket, access_token, values, "my_tickets_history", False, **kwargs
        )

    def _ticket_get_searchbar_sortings(self):
        return {
            "date": {
                "label": _("Newest"),
                "order": "create_date desc",
                "sequence": 1,
            },
            "name": {"label": _("Title"), "order": "name", "sequence": 2},
            "stage": {"label": _("Stage"), "order": "stage_id", "sequence": 3},
            "update": {
                "label": _("Last Stage Update"),
                "order": "last_stage_update desc",
                "sequence": 4,
            },
        }

    def _ticket_get_searchbar_groupby(self):
        values = {
            "none": {"input": "none", "label": _("None"), "order": 1},
            "category": {
                "input": "category",
                "label": _("Category"),
                "order": 2,
            },
            "stage": {"input": "stage", "label": _("Stage"), "order": 3},
        }
        return dict(sorted(values.items(), key=lambda item: item[1]["order"]))

    def _ticket_get_searchbar_inputs(self):
        values = {
            "all": {"input": "all", "label": _("Search in All"), "order": 1},
            "number": {
                "input": "number",
                "label": _("Search in Number"),
                "order": 2,
            },
            "name": {
                "input": "name",
                "label": _("Search in Title"),
                "order": 3,
            },
        }
        return dict(sorted(values.items(), key=lambda item: item[1]["order"]))

    def _ticket_get_search_domain(self, search_in, search):
        search_domain = []
        if search_in in ("number", "all"):
            search_domain.append([("number", "ilike", search)])
        if search_in in ("name", "all"):
            search_domain.append([("name", "ilike", search)])
        return OR(search_domain)

    def _ticket_get_groupby_mapping(self):
        return {
            "category": "category_id",
            "stage": "stage_id",
        }

    def _ticket_get_order(self, order, groupby):
        groupby_mapping = self._ticket_get_groupby_mapping()
        field_name = groupby_mapping.get(groupby, "")
        if not field_name:
            return order
        return "%s, %s" % (field_name, order)
