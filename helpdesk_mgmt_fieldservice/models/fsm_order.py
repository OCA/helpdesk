# Copyright (C) 2019 - TODAY, Open Source Integrators
# Copyright 2020 - TODAY, Marcel Savegnago - Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    ticket_id = fields.Many2one("helpdesk.ticket", string="Ticket", tracking=True)

    def action_complete(self):
        res = super().action_complete()
        if self.ticket_id:
            open_fsm_orders_count = self.env["fsm.order"].search_count(
                [
                    ("ticket_id", "=", self.ticket_id.id),
                    ("stage_id.is_closed", "=", False),
                ]
            )

            if self.ticket_id.stage_id.closed:
                return res
            elif open_fsm_orders_count == 0:
                view_id = self.env.ref(
                    "helpdesk_mgmt_fieldservice.fsm_order_close_wizard_view_form"
                ).id
                return {
                    "view_id": view_id,
                    "view_mode": "form",
                    "res_model": "fsm.order.close.wizard",
                    "type": "ir.actions.act_window",
                    "target": "new",
                    "context": {
                        "default_ticket_id": self.ticket_id.id,
                        "default_team_id": self.ticket_id.team_id.id,
                        "default_resolution": self.resolution,
                    },
                }
            else:
                return res
        else:
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
