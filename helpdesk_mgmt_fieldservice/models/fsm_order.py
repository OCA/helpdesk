# Copyright (C) 2019 - TODAY, Open Source Integrators
# Copyright 2020 - TODAY, Marcel Savegnago - Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    ticket_id = fields.Many2one("helpdesk.ticket", string="Ticket", tracking=True)

    def action_complete(self):
        res = super().action_complete()
        if (
            not self.ticket_id.stage_id.closed
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
                    "default_team_id": self.ticket_id.team_id.id,
                    "default_resolution": self.resolution,
                },
            }
        return res
