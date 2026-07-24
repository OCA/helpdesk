# Copyright 2017 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    helpdesk_ticket_allowed = fields.Boolean(
        related="picking_type_id.allow_helpdesk_ticket"
    )
    helpdesk_tickets_count = fields.Integer(
        compute="_compute_helpdesk_tickets_count",
        help="This is the amount of tickets concerned by this picking.",
    )
    helpdesk_ticket_ids = fields.One2many(
        comodel_name="helpdesk.ticket",
        inverse_name="stock_picking_id",
    )

    @api.depends("helpdesk_ticket_ids")
    def _compute_helpdesk_tickets_count(self):
        """
        Compute the amount of helpesk tickets for those pickings
        """
        domain = [("stock_picking_id", "in", self.ids)]
        results = self.env["helpdesk.ticket"].read_group(
            domain, ["stock_picking_id"], ["stock_picking_id"]
        )
        counts = {
            r["stock_picking_id"][0]: r["stock_picking_id_count"] for r in results
        }
        for picking in self:
            picking.helpdesk_tickets_count = counts.get(picking.id, 0)

    def action_view_helpdesk_tickets(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "helpdesk_mgmt.helpdesk_ticket_action"
        )
        action["domain"] = [("stock_picking_id", "=", self.id)]
        action["context"] = {
            "default_partner_id": self.partner_id.id,
            "default_stock_picking_id": self.id,
        }
        return action

    def _action_open_helpdesk_create_ticket_wizard(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "stock.helpdesk.ticket.create",
            "view_type": "form",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_partner_id": self.partner_id.id,
                "default_stock_picking_id": self.id,
            },
        }

    def create_or_show_helpdesk_ticket(self):
        """Show existing ticket or offer to create a new one."""
        self.ensure_one()
        if not self.helpdesk_tickets_count:
            return self._action_open_helpdesk_create_ticket_wizard()
        return self.action_view_helpdesk_tickets()
