# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, api, fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    account_move_ids = fields.Many2many("account.move")
    account_move_count = fields.Integer(
        compute="_compute_account_move_count", store=True
    )

    @api.depends("account_move_ids")
    def _compute_account_move_count(self):
        groups = self.env["account.move"].read_group(
            domain=[("ticket_ids", "in", self.ids)],
            fields=["ticket_ids"],
            groupby=["ticket_ids"],
        )
        count_by_ticket_id = {
            group["ticket_ids"][0]: group["ticket_ids_count"]
            for group in groups
            if group["ticket_ids"]
        }

        for ticket in self:
            ticket.account_move_count = count_by_ticket_id.get(ticket.id, 0)

    def action_view_account_moves(self):
        action = {
            "name": "Account Moves",
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "view_mode": "tree,form",
            "target": "current",
        }

        action["domain"] = [("ticket_ids", "in", [self.id])]
        action["context"] = {
            "default_ticket_ids": [Command.link(self.id)],
            "default_partner_id": self.partner_id.id,
        }
        return action
