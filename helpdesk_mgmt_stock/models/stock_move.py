# Copyright 2018 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    helpdesk_ticket_count = fields.Integer(compute="_compute_helpdesk_ticket_count")
    helpdesk_ticket_ids = fields.One2many(
        comodel_name="helpdesk.ticket",
        inverse_name="stock_move_id",
    )

    @api.depends("helpdesk_ticket_ids")
    def _compute_helpdesk_ticket_count(self):
        domain = [("stock_move_id", "in", self.ids)]
        results = self.env["helpdesk.ticket"]._read_group(
            domain, ["stock_move_id"], ["__count"]
        )
        counts = dict(results)
        for move in self:
            move.helpdesk_ticket_count = counts.get(move, 0)

    def action_view_helpdesk_tickets(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "helpdesk_mgmt.helpdesk_ticket_action"
        )
        action["domain"] = [("stock_move_id", "=", self.id)]
        action["context"] = {
            "default_stock_move_id": self.id,
            "default_stock_picking_id": self.picking_id.id,
        }
        if self.helpdesk_ticket_count == 1:
            action.update(
                {
                    "res_id": self.helpdesk_ticket_ids.id,
                    "views": [(False, "form")],
                }
            )
        return action

    def _action_open_helpdesk_create_ticket_wizard(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "stock.helpdesk.ticket.create",
            "view_type": "form",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_stock_move_id": self.id,
                "default_stock_picking_id": self.picking_id.id,
            },
        }

    def create_or_show_helpdesk_ticket(self):
        """Show existing ticket or offer to create a new one."""
        self.ensure_one()
        if not self.helpdesk_ticket_count:
            return self._action_open_helpdesk_create_ticket_wizard()
        return self.action_view_helpdesk_tickets()
