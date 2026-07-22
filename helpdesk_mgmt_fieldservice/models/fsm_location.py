# Copyright (C) 2019 - TODAY, Open Source Integrators
# Copyright 2020 - TODAY, Marcel Savegnago - Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMLocation(models.Model):
    _inherit = "fsm.location"

    ticket_count = fields.Integer(
        compute="_compute_ticket_count",
        string="# Tickets",
    )
    ticket_ids = fields.One2many(
        "helpdesk.ticket",
        "fsm_location_id",
        string="Helpdesk Tickets",
        readonly=True,
    )

    def _compute_ticket_count(self):
        counts = dict(
            self.env["helpdesk.ticket"]._read_group(
                domain=[("fsm_location_id", "in", self.ids)],
                groupby=["fsm_location_id"],
                aggregates=["__count"],
            )
        )
        for rec in self:
            rec.ticket_count = counts.get(rec, 0)

    def action_view_ticket(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "helpdesk_mgmt.helpdesk_ticket_action"
        )
        action["context"] = {
            "search_default_open": 1,
            "default_fsm_location_id": len(self) == 1 and self.id,
            "default_partner_id": len(self.partner_id) == 1 and self.partner_id.id,
        }
        if len(self.ticket_ids) == 1:
            action["views"] = [(False, "form")]
            action["res_id"] = self.ticket_ids.id
        else:
            action["domain"] = [("fsm_location_id", "in", self.ids)]
        return action
