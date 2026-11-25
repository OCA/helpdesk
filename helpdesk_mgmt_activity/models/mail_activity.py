# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MailActivity(models.Model):
    _inherit = "mail.activity"

    ticket_id = fields.Many2one(
        comodel_name="helpdesk.ticket",
        help="Activity created from helpdesk ticket"
        "After closing this activity, ticket is moved to done stage",
    )

    def _action_done(self, feedback=False, attachment_ids=None):
        # Get closed stage for ticket
        for ticket in self.ticket_id:
            if ticket.team_id and ticket.team_id.activity_stage_id:
                # Change ticket stage
                ticket.stage_id = ticket.team_id.activity_stage_id.id
        return super()._action_done(feedback, attachment_ids)
