from odoo import api, fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    duplicate_id = fields.Many2one(
        "helpdesk.ticket", string="Duplicte of", tracking=True
    )
    duplicate_ids = fields.One2many(
        "helpdesk.ticket", "duplicate_id", string="Duplicate tickets"
    )
    duplicate_count = fields.Integer(compute="_compute_duplicate_count")

    @api.depends("duplicate_ids")
    def _compute_duplicate_count(self):
        for record in self:
            record.duplicate_count = len(record.duplicate_ids)

    def action_open_duplicate_wizard(self):
        self.ensure_one()
        duplicate_stage = self.env.ref(
            "helpdesk_ticket_duplicate.helpdesk_ticket_stage_duplicate"
        )
        return {
            "name": "Mark as Duplicate",
            "type": "ir.actions.act_window",
            "res_model": "helpdesk.ticket.duplicate.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_ticket_id": self.id,
                "default_target_stage_id": duplicate_stage.id,
            },
        }

    def action_view_duplicates(self):
        self.ensure_one()
        return {
            "name": "Duplicates",
            "type": "ir.actions.act_window",
            "res_model": "helpdesk.ticket",
            "view_mode": "list",
            "target": "new",
            "domain": [("duplicate_id", "=", self.id)],
        }
