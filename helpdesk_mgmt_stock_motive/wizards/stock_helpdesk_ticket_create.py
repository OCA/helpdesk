# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockHelpdeskTicketCreate(models.TransientModel):
    _inherit = "stock.helpdesk.ticket.create"

    motive_id = fields.Many2one("helpdesk.ticket.motive")

    def _prepare_ticket_values(self) -> dict:
        vals = super()._prepare_ticket_values()
        vals["motive_id"] = self.motive_id.id
        return vals
