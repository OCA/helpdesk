# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.osv.expression import TRUE_DOMAIN


class HelpdeskTicket(models.Model):

    _inherit = "helpdesk.ticket"

    stock_move_id_domain = fields.Binary(compute="_compute_stock_move_id_domain")
    stock_move_id = fields.Many2one(
        comodel_name="stock.move",
        string="Stock Move",
        ondelete="restrict",
        index="btree_not_null",
    )
    stock_picking_id = fields.Many2one(
        comodel_name="stock.picking",
        string="Stock Picking",
        ondelete="restrict",
        index="btree_not_null",
    )
    lot_id = fields.Many2one(
        comodel_name="stock.lot",
        related="stock_move_id.move_line_ids.lot_id",
        readonly=True,
    )

    @api.depends("stock_picking_id")
    def _compute_stock_move_id_domain(self):
        picking_records = self.filtered("stock_picking_id")
        without_picking_records = self - picking_records
        for ticket in picking_records:
            if ticket.stock_picking_id:
                ticket.stock_move_id_domain = [
                    ("picking_id", "=", ticket.stock_picking_id.id)
                ]
        if without_picking_records:
            without_picking_records.stock_move_id_domain = TRUE_DOMAIN

    @api.model
    def show_existing_stock_tickets(self, domain):
        """Show the helpdesk tickets for a specific domain."""
        action_data = self.env["ir.actions.act_window"]._for_xml_id(
            "helpdesk_mgmt.helpdesk_ticket_action"
        )
        action_data["domain"] = domain
        return action_data
