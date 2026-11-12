# Copyright (C) 2019 - TODAY, Open Source Integrators
# Copyright 2020 - TODAY, Marcel Savegnago - Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.exceptions import AccessError


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    ticket_id = fields.Many2one("helpdesk.ticket", string="Ticket", tracking=True)

    def _check_tickets_access(self):
        """The current user can access the tickets of `self`."""
        tickets = self.ticket_id
        try:
            tickets.check_access_rights("write")
            tickets.check_access_rule("write")
        except AccessError:
            can_access_tickets = False
        else:
            can_access_tickets = True
        return can_access_tickets

    def action_complete(self):
        res = super().action_complete()
        if (
            self._check_tickets_access()
            and not self.ticket_id.stage_id.closed
            and self.ticket_id.fsm_order_ids
            and all(self.ticket_id.mapped("fsm_order_ids.stage_id.is_closed"))
        ):
            return {
                "view_mode": "form",
                "res_model": "fsm.order.close.wizard",
                "type": "ir.actions.act_window",
                "target": "new",
                "context": {
                    "default_ticket_id": self.ticket_id.id,
                    "default_resolution": self.resolution,
                },
            }
        return res

    def action_view_order(self):
        """
        This function returns an action that displays a full FSM Order
        form when viewing an FSM Order from a ticket.
        """
        action = self.env["ir.actions.actions"]._for_xml_id(
            "fieldservice.action_fsm_operation_order"
        )
        order = self.env["fsm.order"].search([("id", "=", self.id)])
        action["views"] = [
            (self.env.ref("fieldservice." + "fsm_order_form").id, "form")
        ]
        action["res_id"] = order.id
        return action
