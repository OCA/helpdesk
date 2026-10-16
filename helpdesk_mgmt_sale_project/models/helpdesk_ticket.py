# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    # NOTE: Field defined in `helpdesk_mgmt_project`, make it computed
    project_id = fields.Many2one(
        compute="_compute_project_id", store=True, readonly=False
    )

    @api.depends("sale_order_ids.project_id")
    def _compute_project_id(self):
        # pylint: disable=missing-return
        if hasattr(super(), "_compute_project_id"):
            super()._compute_project_id()
        for ticket in self:
            if (
                not ticket.project_id
                and len(project := ticket.sale_order_ids.project_id) == 1
            ):
                ticket.project_id = project

    @api.constrains("sale_order_ids", "project_id")
    def _check_unique_project(self):
        for ticket in self:
            projects = ticket.mapped("sale_order_ids.project_id")
            if len(projects) > 1:
                raise ValidationError(
                    self.env._(
                        "Ticket '%s' cannot have multiple different projects.",
                        ticket.name,
                    )
                )
