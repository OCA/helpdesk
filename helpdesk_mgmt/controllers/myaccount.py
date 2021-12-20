# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.exceptions import AccessError

from odoo.osv.expression import OR


class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        ticket_count = (
            request.env["helpdesk.ticket"].search_count([])
            if request.env["helpdesk.ticket"].check_access_rights(
                "read", raise_exception=False
            )
            else 0
        )
        values['ticket_count'] = ticket_count
        return values

    def _helpdesk_ticket_check_access(self, ticket_id):
        ticket = request.env['helpdesk.ticket'].browse([ticket_id])
        ticket_sudo = ticket.sudo()
        try:
            ticket.check_access_rights('read')
            ticket.check_access_rule('read')
        except AccessError:
            raise
        return ticket_sudo

    def _message_content_field_exists(self):
        base_search_module = request.env['ir.module.module'].sudo().search([
            ('name', '=', 'base_search_mail_content')])
        return (base_search_module and base_search_module.state == 'installed')

    @http.route(
        ['/my/tickets', '/my/tickets/page/<int:page>'],
        type='http',
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
            search_in='all',
            **kw):
        values = self._prepare_portal_layout_values()
        HelpdesTicket = request.env['helpdesk.ticket']
        domain = []

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'stage_id'},
            'update': {'label': _('Last Stage Update'),
                       'order': 'last_stage_update desc'},
        }

        # search input (text)
        searchbar_inputs = {
            'name': {'input': 'name',
                     'label': _('Search in Names')},
            'description': {'input': 'description',
                            'label': _('Search in Descriptions')},
            'user_id': {'input': 'user',
                        'label': _('Search in Assigned users')},
            'category_id': {'input': 'category',
                            'label': _('Search in Categories')},
        }
        if self._message_content_field_exists():
            searchbar_inputs['message_content'] = {
                'input': 'message_content',
                'label': _('Search in Messages')
            }
        searchbar_meta_inputs = {
            'content': {'input': 'content', 'label': _('Search in Content')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }

        if search and search_in:
            search_domain = []
            if search_in == 'content':
                search_domain = ['|', ('name', 'ilike', search),
                                 ('description', 'ilike', search)]

                if 'message_content' in searchbar_inputs:
                    search_domain = OR([
                        search_domain,
                        [('message_content', 'ilike', search)]
                    ])
            else:
                for search_property in [
                        k
                        for (k, v) in searchbar_inputs.items()
                        if search_in in (v['input'], 'all')
                ]:
                    search_domain = OR(
                        [search_domain, [(search_property, 'ilike', search)]])
            domain += search_domain
        searchbar_inputs.update(searchbar_meta_inputs)

        # search filters (by stage)
        searchbar_filters = {'all': {'label': _('All'), 'domain': []}}
        for stage in request.env['helpdesk.ticket.stage'].search([]):
            searchbar_filters.update({
                str(stage.id): {'label': stage.name,
                                'domain': [('stage_id', '=', stage.id)]}
            })

        # default sort by order
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        # count for pager
        ticket_count = HelpdesTicket.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/tickets",
            url_args={},
            total=ticket_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        tickets = HelpdesTicket.search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager['offset']
        )
        values.update({
            'date': date_begin,
            'tickets': tickets,
            'page_name': 'ticket',
            'pager': pager,
            'default_url': '/my/tickets',
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'sortby': sortby,
            'searchbar_filters': searchbar_filters,
            'filterby': filterby,
        })
        return request.render("helpdesk_mgmt.portal_my_tickets", values)

    @http.route(['/my/ticket/<int:ticket_id>'], type='http', website=True)
    def portal_my_ticket(self, ticket_id=None, **kw):
        try:
            ticket_sudo = self._helpdesk_ticket_check_access(ticket_id)
        except AccessError:
            return request.redirect('/my')
        values = self._ticket_get_page_view_values(ticket_sudo, **kw)
        return request.render("helpdesk_mgmt.portal_helpdesk_ticket_page",
                              values)

    def _ticket_get_page_view_values(self, ticket, **kwargs):
        closed_stages = request.env['helpdesk.ticket.stage'].search(
            [('closed', '=', True)])
        files = request.env['ir.attachment'].search(
            [('res_model', '=', 'helpdesk.ticket'), ('res_id', '=', ticket.id)])
        values = {
            'page_name': 'ticket',
            'ticket': ticket,
            'closed_stages': closed_stages,
            "files": files,
        }

        if kwargs.get('error'):
            values['error'] = kwargs['error']
        if kwargs.get('warning'):
            values['warning'] = kwargs['warning']
        if kwargs.get('success'):
            values['success'] = kwargs['success']

        return values
