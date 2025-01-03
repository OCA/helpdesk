# Copyright 2024 Antoni Marroig(APSL-Nagarro)<amarroig@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    related_ticket_ids = fields.Many2many(
        "helpdesk.ticket",
        "ticket_relationship_table",
        "ticket_id1",
        "ticket_id2",
        string="Related tickets",
    )

    def write(self, vals):
        if "related_ticket_ids" in vals:
            for ticket in self.related_ticket_ids:
                if (
                    6 == vals.get("related_ticket_ids")[0][0]
                    and ticket.id not in vals.get("related_ticket_ids")[0][2]
                ):
                    ticket.write({"related_ticket_ids": [(3, self.id)]})
        res = super().write(vals)
        if "related_ticket_ids" in vals:
            for rel_ticket in self.related_ticket_ids:
                if self._origin.id not in rel_ticket.related_ticket_ids.ids:
                    rel_ticket.write({"related_ticket_ids": [(4, self.id)]})
        return res

    def open_ticket(self):
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "helpdesk.ticket",
            "res_id": self.id,
        }
