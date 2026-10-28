# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HelpdeskTicketMotive(models.Model):
    _inherit = "helpdesk.ticket.motive"

    location_dest_id = fields.Many2one(
        "stock.location", string="Destination Location", ondelete="restrict"
    )
