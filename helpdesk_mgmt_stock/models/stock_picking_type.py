# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingType(models.Model):

    _inherit = "stock.picking.type"

    allow_helpdesk_ticket = fields.Boolean(
        help="Check this if you want to authorize helpdesk ticket creation"
        "for this picking type operations."
    )
    default_helpdesk_team_id = fields.Many2one(
        comodel_name="helpdesk.ticket.team",
        help="Fill in this with the team to assign to when creating tickets.",
    )
