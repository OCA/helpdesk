# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    nonconformity_id = fields.Many2one(
        comodel_name="mgmtsystem.nonconformity",
        string="Nonconformity",
    )

    def _prepare_nonconformity_vals(self):
        stage = self.stage_id.nonconformity_stage_id or self.env.ref(
            "mgmtsystem_nonconformity.stage_draft"
        )
        vals = {
            "ticket_ids": [(6, 0, self.ids)],
            "name": self.name,
            "partner_id": self.partner_id.id,
            "stage_id": stage.id,
            "user_id": self.user_id.id,
            "manager_user_id": self.team_id.user_id.id or self.user_id.id,
            "responsible_user_id": self.team_id.user_id.id or self.user_id.id,
            "description": self.description,
        }
        if stage.state == "open":
            vals.update({"action_comments": self.description})
        elif stage.state == "done":
            vals.update({"evaluation_comments": self.description})
        return vals

    def action_nonconformity_create(self):
        if self.filtered("nonconformity_id"):
            raise UserError(_("There are already linked nonconformities."))
        nonconformity_model = self.env["mgmtsystem.nonconformity"].with_context(
            skip_stage_change=True
        )
        for item in self:
            item.nonconformity_id = nonconformity_model.create(
                item._prepare_nonconformity_vals()
            )

    def action_open_nonconformity(self):
        return {
            "name": _("Nonconformity"),
            "view_mode": "form",
            "res_model": "mgmtsystem.nonconformity",
            "res_id": self.nonconformity_id.id,
            "type": "ir.actions.act_window",
            "context": dict(self._context, create=False),
        }

    def write(self, vals):
        res = super().write(vals)
        if vals.get("stage_id") and not self.env.context.get("skip_stage_change"):
            items = self.mapped("nonconformity_id")
            stage = self.env["helpdesk.ticket.stage"].browse(vals.get("stage_id"))
            if stage.nonconformity_stage_id and items:
                items.with_context(skip_stage_change=True).write(
                    {"stage_id": stage.nonconformity_stage_id.id}
                )
        return res
