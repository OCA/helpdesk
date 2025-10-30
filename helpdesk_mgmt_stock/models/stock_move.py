# Copyright 2018 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class StockMove(models.Model):

    _inherit = "stock.move"

    helpdesk_tickets_count = fields.Integer(compute="_compute_helpdesk_tickets_count")
    helpdesk_ticket_ids = fields.One2many(
        comodel_name="helpdesk.ticket",
        inverse_name="stock_move_id",
    )

    @api.depends("helpdesk_ticket_ids")
    def _compute_helpdesk_tickets_count(self):
        domain = [("stock_move_id", "in", self.ids)]
        results = self.env["helpdesk.ticket"].read_group(
            domain, ["stock_move_id"], ["stock_move_id"]
        )
        counts = {r["stock_move_id"][0]: r["stock_move_id_count"] for r in results}
        for move in self:
            move.helpdesk_tickets_count = counts.get(move.id, 0)

    def create_or_show_helpdesk_ticket(self):
        """Show existing ticket or offer to create a new one."""
        self.ensure_one()
        if not self.helpdesk_tickets_count:
            return {
                "type": "ir.actions.act_window",
                "res_model": "stock.helpdesk.ticket.create",
                "view_type": "form",
                "view_mode": "form",
                "target": "new",
            }

        return self.env["helpdesk.ticket"].show_existing_stock_tickets(
            [("stock_move_id", "=", self.id)]
        )
