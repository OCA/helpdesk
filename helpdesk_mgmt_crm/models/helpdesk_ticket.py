# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    lead_ids = fields.One2many(
        comodel_name="crm.lead",
        inverse_name="ticket_id",
        string="Opportunity(ies)",
    )
    lead_count = fields.Integer(
        compute="_compute_lead_count", string="Opportunity Count"
    )

    @api.depends("lead_ids")
    def _compute_lead_count(self):
        lead_data = self.env["crm.lead"]._read_group(
            [("ticket_id", "in", self.ids)],
            groupby=["ticket_id"],
            aggregates=["__count"],
        )
        mapped_data = {ticket.id: count for ticket, count in lead_data}
        for item in self:
            item.lead_count = mapped_data.get(item.id, 0)

    def action_open_leads(self):
        action = self.lead_ids._get_records_action(name=self.env._("Opportunity(ies)"))
        action["context"].update(
            {"default_ticket_id": self.id, "search_default_ticket_id": self.id}
        )
        return action
