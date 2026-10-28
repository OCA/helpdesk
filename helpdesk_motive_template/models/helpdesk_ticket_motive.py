# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HelpdeskTicketMotive(models.Model):
    _inherit = "helpdesk.ticket.motive"

    description_template = fields.Html(
        sanitize_style=True,
        translate=True,
        help="Use dynamic placeholders like {{ ticket.name }}.",
    )
