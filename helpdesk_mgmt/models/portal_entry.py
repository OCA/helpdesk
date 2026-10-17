# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class PortalEntry(models.Model):
    _inherit = "portal.entry"

    def _filter_visible_portal_cards(self):
        """Keep the tickets card visible even when the customer has none yet."""
        visible_entries = super()._filter_visible_portal_cards()
        tickets_entry = self.env.ref(
            "helpdesk_mgmt.portal_entry_tickets", raise_if_not_found=False
        )
        if tickets_entry:
            visible_entries |= self & tickets_entry
        return visible_entries
