# Copyright (C) 2019 - TODAY, Open Source Integrators
# Copyright (C) 2022 - TODAY, Popsolutions
# Copyright (C) 2022 - TODAY, Mateus ONunes
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    fsm_equipment_id = fields.Many2one("fsm.equipment", string="FSM Equipment")

    def action_create_order(self):
        """
        This function returns an action that displays a full FSM Order
        form when creating an FSM Order from a ticket.
        """
        action = self.env["ir.actions.actions"]._for_xml_id(
            "fieldservice.action_fsm_operation_order"
        )
        # override the context to get rid of the default filtering
        action["context"] = {
            "default_ticket_id": self.id,
            "default_priority": self.priority,
            "default_location_id": self.fsm_location_id.id,
            "default_equipment_id": self.fsm_equipment_id.id,
            "type": 1 # Maintenance
        }
        res = self.env.ref("fieldservice.fsm_order_form", False)
        action["views"] = [(res and res.id or False, "form")]
        return action

