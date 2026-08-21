# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    ticket_ids = fields.Many2many("helpdesk.ticket")
    ticket_count = fields.Integer(
        string="Tickets Count", compute="_compute_ticket_count", store=True
    )

    @api.depends("ticket_ids")
    def _compute_ticket_count(self):
        groups = self.env["helpdesk.ticket"].read_group(
            domain=[("account_move_ids", "in", self.ids)],
            fields=["account_move_ids"],
            groupby=["account_move_ids"],
        )

        count_by_move_id = {
            group["account_move_ids"][0]: group["account_move_ids_count"]
            for group in groups
            if group["account_move_ids"]
        }

        for move in self:
            move.ticket_count = count_by_move_id.get(move.id, 0)

    def action_view_helpdesk_tickets(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "helpdesk_mgmt.helpdesk_ticket_action"
        )
        action["domain"] = [("account_move_ids", "in", [self.id])]
        action["context"] = {
            "default_account_move_ids": [Command.set(self.ids)],
            # ↓ enables to show the "1" in smart button even before save
            "default_account_move_count": 1,
        }
        return action
