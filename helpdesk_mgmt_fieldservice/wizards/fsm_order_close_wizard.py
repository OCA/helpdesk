# Copyright (C) 2019 Pavlov Media
# Copyright 2020 - TODAY, Marcel Savegnago - Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMOrderCloseWizard(models.TransientModel):
    _name = "fsm.order.close.wizard"
    _description = "FSM Close - Option to Close Ticket"

    resolution = fields.Text()
    team_id = fields.Many2one("helpdesk.ticket.team", string="Helpdesk Team")
    stage_id = fields.Many2one("helpdesk.ticket.stage", string="Stage")
    ticket_id = fields.Many2one("helpdesk.ticket", string="Ticket")

    def action_close_ticket(self):
        for record in self:
            if not record.ticket_id.stage_id.closed:
                record.ticket_id.write(
                    {"resolution": record.resolution, "stage_id": record.stage_id.id}
                )
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }
