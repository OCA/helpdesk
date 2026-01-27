# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import models


class ProjectTask(models.Model):
    _inherit = "project.task"

    def write(self, vals):
        result = super().write(vals)
        if "stage_id" in vals:
            for this in self:
                this.sudo()._set_stage_ticket()
        return result

    def _set_stage_ticket(self):
        self.ensure_one()
        for ticket in self.ticket_ids:
            new_stage = (
                self.stage_id.ticket_stage_ids & ticket.team_id._get_applicable_stages()
            )[:1]
            if new_stage and ticket.stage_id != new_stage:
                if (
                    ticket.stage_id.sync_limit_single_task
                    or new_stage.sync_limit_single_task
                ):
                    task_count = self.env["project.task"].search_count(
                        [("ticket_ids", "in", ticket.id)]
                    )
                    ticket_count = len(self.ticket_ids)
                    if task_count != 1 or ticket_count != 1:
                        continue
                ticket.stage_id = new_stage
