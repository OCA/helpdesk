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
        for milestone in self:
            milestone.helpdesk_ticket_count = len(milestone.helpdesk_ticket_ids)

    def action_view_helpdesk_ticket(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "helpdesk_mgmt_project.action_view_helpdesk_ticket_for_milestone"
        )
        action["context"] = {
            "default_project_id": self.project_id.id,
            "default_milestone_id": self.id,
        }
        if self.helpdesk_ticket_count == 1:
            action["view_mode"] = "form"
            action["res_id"] = self.helpdesk_ticket_ids.id
            if "views" in action:
                action["views"] = [
                    (view_id, view_type)
                    for view_id, view_type in action["views"]
                    if view_type == "form"
                ]
        return action
