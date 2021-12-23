# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _
from odoo.osv.expression import OR

from odoo.addons.helpdesk_mgmt.controllers.myaccount import CustomerPortalHelpdesk


class CustomerPortalHelpdesk(CustomerPortalHelpdesk):
    def _get_portal_searchbar_inputs(self):
        searchbar_inputs = super(
            CustomerPortalHelpdesk, self
        )._get_portal_searchbar_inputs()
        searchbar_inputs["message_content"] = {
            "input": "message_content",
            "label": _("Search in Messages"),
        }
        return searchbar_inputs

    def _get_search_in_content_domain(self, search):
        search_domain = super(
            CustomerPortalHelpdesk, self
        )._get_search_in_content_domain(search)

        return OR([search_domain, [("message_content", "ilike", search)]])
