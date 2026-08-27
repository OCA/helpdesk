# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MgmtsystemNonconformity(models.Model):
    _inherit = "mgmtsystem.nonconformity"

    ticket_ids = fields.One2many(
        comodel_name="helpdesk.ticket",
        inverse_name="nonconformity_id",
        string="Tickets",
    )
    ticket_count = fields.Integer(compute="_compute_ticket_count")

    @api.depends("ticket_ids")
    def _compute_ticket_count(self):
        ticket_data = self.env["helpdesk.ticket"].read_group(
            [("nonconformity_id", "in", self.ids)],
            ["nonconformity_id"],
            ["nonconformity_id"],
        )
        mapped_data = {
            t["nonconformity_id"][0]: t["nonconformity_id_count"] for t in ticket_data
        }
        for item in self:
            item.ticket_count = mapped_data.get(item.id, 0)

    def write(self, vals):
        res = super().write(vals)
        if vals.get("stage_id") and not self.env.context.get("skip_stage_change"):
            ticket_stage = self.env["helpdesk.ticket.stage"].search(
                [("nonconformity_stage_id", "=", vals.get("stage_id"))], limit=1
            )
            if ticket_stage and self.ticket_ids:
                self.ticket_ids.with_context(skip_stage_change=True).write(
                    {"stage_id": ticket_stage.id}
                )
        return res
