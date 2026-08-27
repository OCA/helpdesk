# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HelpdeskTicketStage(models.Model):
    _inherit = "helpdesk.ticket.stage"

    nonconformity_stage_id = fields.Many2one(
        comodel_name="mgmtsystem.nonconformity.stage",
        string="Nonconformity Stage",
    )
