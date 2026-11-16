# Copyright (C) 2019 - TODAY, Open Source Integrators
# Copyright 2020 - TODAY, Marcel Savegnago - Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    ticket_id = fields.Many2one("helpdesk.ticket", string="Ticket", tracking=True)

    def action_complete(self):
        res = super().action_complete()
        tickets = self.ticket_id
        if (
            tickets.has_access("write")
            and not tickets.stage_id.closed
            and tickets.fsm_order_ids
            and all(tickets.mapped("fsm_order_ids.stage_id.is_closed"))
        ):
            return {
                "view_mode": "form",
                "res_model": "fsm.order.close.wizard",
                "type": "ir.actions.act_window",
                "target": "new",
                "context": {
                    "default_ticket_id": tickets.id,
                    "default_resolution": self.resolution,
                },
            }
        return res
