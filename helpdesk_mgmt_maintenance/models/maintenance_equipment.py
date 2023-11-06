# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class MaintenanceEquipment(models.Model):
    _inherit = "maintenance.equipment"

    ticket_ids = fields.Many2many(
        "helpdesk.ticket",
        string="Tickets",
        relation="helpdesk_ticket_maintenance_equipment_rel",
        column1="maintenance_equipment_id",
        column2="helpdesk_ticket_id",
        copy=False,
    )

    allow_ticket = fields.Boolean(string="Allow Tickets", default=False)

    # NUMBERS TICKETS COMPUTE NO STORE

    ticket_count = fields.Integer(
        string="Number Tickets", compute="_compute_ticket_count"
    )

    def _compute_ticket_count(self):
        number_tickets = self.env["helpdesk.ticket"].read_group(
            [("equipment_ids", "in", self.ids)], ["equipment_ids"], ["equipment_ids"]
        )
        result = {
            data["equipment_ids"][0]: data["equipment_ids_count"]
            for data in number_tickets
        }
        for equipment in self:
            equipment.ticket_count = result.get(equipment.id, 0)

    def action_view_tickets_equipment(self):
        return {
            "name": ("Tickets"),
            "res_model": "helpdesk.ticket",
            "view_mode": "tree,kanban,form",
            "type": "ir.actions.act_window",
            "domain": [("id", "in", self.ticket_ids.ids)],
            "context": {
                "default_equipment_ids": [(4, self.id)],
            },
        }
