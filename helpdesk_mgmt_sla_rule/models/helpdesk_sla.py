# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class HelpDeskTicket(models.Model):
    _inherit = "helpdesk.sla"

    def check_sla(self):
        tickets = self.env["helpdesk.ticket"].search([("sla_id", "!=", False)])
        for ticket in tickets:
            ticket.sla_id.check_ticket_sla(ticket)
