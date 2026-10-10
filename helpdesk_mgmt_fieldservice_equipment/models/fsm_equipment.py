# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMEquipment(models.Model):
    _inherit = "fsm.equipment"

    helpdesk_ticket_ids = fields.One2many("helpdesk.ticket", "equipment_id")
    helpdesk_ticket_count = fields.Integer(compute="_compute_helpdesk_ticket_count")

    def _compute_helpdesk_ticket_count(self):
        counts = dict(
            self.env["helpdesk.ticket"]._read_group(
                domain=[("equipment_id", "in", self.ids)],
                groupby=["equipment_id"],
                aggregates=["__count"],
            )
        )
        for record in self:
            record.helpdesk_ticket_count = counts.get(record, 0)

    def action_view_helpdesk_tickets(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "helpdesk_mgmt.helpdesk_ticket_action"
        )
        # Without id and path the client restores this action on reload,
        # instead of loading the menu action again without the domain.
        action.update(
            id=False,
            path=False,
            domain=[("equipment_id", "=", self.id)],
            context={
                "default_equipment_id": self.id,
                "default_fsm_location_id": self.location_id.id,
            },
        )
        return action
