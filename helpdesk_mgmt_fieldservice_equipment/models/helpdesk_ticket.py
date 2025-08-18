# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class HelpDeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    equipment_id = fields.Many2one(
        comodel_name="fsm.equipment",
        string="Equipment",
        help="Equipment that is used for the helpdesk ticket.",
        domain="['|', "
        "('location_id', '=', False), "
        "('location_id', '=?', fsm_location_id)]",
        required=False,
        copy=False,
    )
    equipment_stage_id = fields.Many2one(
        comodel_name="fsm.stage",
        related="equipment_id.stage_id",
        readonly=False,
        string="Equipment stage",
        domain="[('stage_type', '=', 'equipment')]",
        copy=False,
    )

    @api.constrains("fsm_location_id", "equipment_id")
    def _check_equipment_location(self):
        for record in self:
            if (
                record.equipment_id.location_id
                and record.equipment_id.location_id != record.fsm_location_id
            ):
                raise ValidationError(
                    self.env._(
                        "The location of the ticket and equipment are not the same."
                    )
                )

    def action_create_order(self):
        action = super().action_create_order()
        if self.equipment_id:
            action["context"].update(
                {"default_equipment_ids": [(6, 0, [self.equipment_id.id])]}
            )
        return action
