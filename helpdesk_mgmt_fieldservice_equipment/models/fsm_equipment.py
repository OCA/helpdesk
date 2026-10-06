# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMEquipment(models.Model):
    _inherit = "fsm.equipment"

    helpdesk_ticket_ids = fields.One2many("helpdesk.ticket", "equipment_id")
    helpdesk_ticket_count = fields.Integer(compute="_compute_helpdesk_ticket_count")

    @api.depends("helpdesk_ticket_ids")
    def _compute_helpdesk_ticket_count(self):
        for record in self:
            record.helpdesk_ticket_count = len(record.helpdesk_ticket_ids)
