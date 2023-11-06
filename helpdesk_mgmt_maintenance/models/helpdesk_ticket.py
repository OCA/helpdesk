# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    equipment_ids = fields.Many2many(
        "maintenance.equipment",
        string="Equipments",
        relation="helpdesk_ticket_maintenance_equipment_rel",
        column1="helpdesk_ticket_id",
        column2="maintenance_equipment_id",
        copy=False,
    )

    has_equipments = fields.Boolean(store=True, compute="_compute_has_equipments")

    @api.depends("equipment_ids")
    def _compute_has_equipments(self):
        for ticket in self:
            ticket.has_equipments = bool(ticket.equipment_ids)
