# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    account_move_ids = fields.Many2many("account.move")
    account_move_count = fields.Integer(
        compute="_compute_account_move_count", store=True
    )

    @api.depends("account_move_ids")
    def _compute_account_move_count(self):
        for ticket in self:
            ticket.account_move_count = len(ticket.account_move_ids)

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
            "default_ticket_ids": [(4, [self.id])],
            "default_partner_id": self.partner_id.id,
        }
        return action
