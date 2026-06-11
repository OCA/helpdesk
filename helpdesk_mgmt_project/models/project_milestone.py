# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProjectMilestone(models.Model):
    _inherit = "project.milestone"

    helpdesk_ticket_ids = fields.One2many(
        comodel_name="helpdesk.ticket",
        inverse_name="milestone_id",
    )

    helpdesk_ticket_count = fields.Integer(
        compute="_compute_helpdesk_ticket_count",
    )

    @api.depends("helpdesk_ticket_ids")
    def _compute_helpdesk_ticket_count(self):
        counts = {
            milestone.id: count
            for milestone, count in self.env["helpdesk.ticket"]._read_group(
                [("milestone_id", "in", self.ids)], ["milestone_id"], ["__count"]
            )
        }
        for milestone in self:
            milestone.helpdesk_ticket_count = counts.get(milestone.id, 0)

    def action_view_helpdesk_ticket(self):
        self.ensure_one()
        return self.helpdesk_ticket_ids._get_records_action(
            name=self.env._("Helpdesk Tickets"),
            view_mode="kanban,list,form,pivot",
            context={
                "default_project_id": self.project_id.id,
                "default_milestone_id": self.id,
            },
        )
