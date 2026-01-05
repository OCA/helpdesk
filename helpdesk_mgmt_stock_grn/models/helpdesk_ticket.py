# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    grn_id = fields.Many2one(
        related="stock_picking_id.grn_id",
        string="Goods Received Note",
    )
    grn_date = fields.Datetime(
        related="grn_id.date",
        string="GRN Date",
    )
    delivery_note_supplier_number = fields.Char(
        related="grn_id.delivery_note_supplier_number",
        string="Supplier delivery note number",
    )
