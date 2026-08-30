# Copyright 2026 Paloma González-Ripoll(APSL-Nagarro)<paloma.gonzalez@nagarro.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    block_ticket_creation = fields.Boolean(
        string="Block ticket creation by email",
        default=False,
        help="If checked, this contact will not be able to create new "
        "helpdesk tickets by email. An automatic notification email will "
        "be sent instead, using the configured template.",
    )
