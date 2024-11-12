# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HelpdeskTicketStage(models.Model):
    _inherit = "helpdesk.ticket.stage"

    validate_field_ids = fields.Many2many(
        "ir.model.fields",
        string="Fields to Validate",
        help="Select fields which must be set on the document in this stage",
        domain=[("model", "=", "helpdesk.ticket")],
    )
