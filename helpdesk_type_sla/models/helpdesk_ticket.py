#    Copyright (C) 2020 GARCO Consulting <www.garcoconsulting.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    def _get_sla_ticket_domain(self):
        domain = super()._get_sla_ticket_domain()
        if self.type_id:
            domain += [
                "|",
                ("type_ids", "=", False),
                ("type_ids", "in", self.type_id.ids),
            ]
        else:
            domain += [("type_ids", "=", False)]
        return domain
