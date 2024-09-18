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
        lead_data = self.env["crm.lead"].read_group(
            [("ticket_id", "in", self.ids)],
            ["ticket_id"],
            ["ticket_id"],
        )
        mapped_data = {t["ticket_id"][0]: t["ticket_id_count"] for t in lead_data}
        for item in self:
            item.lead_count = mapped_data.get(item.id, 0)

    def action_open_leads(self):
        action = self.env.ref("crm.crm_lead_action_pipeline")
        result = action.read()[0]
        if len(self.lead_ids) == 1:
            res = self.env.ref("crm.crm_lead_view_form", False)
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = self.lead_ids.id
        else:
            result["domain"] = [("id", "in", self.lead_ids.ids)]
            ctx = dict(self.env.context)
            ctx.update(
                {"default_ticket_id": self.id, "search_default_ticket_id": self.id}
            )
            result["context"] = ctx
        return result
