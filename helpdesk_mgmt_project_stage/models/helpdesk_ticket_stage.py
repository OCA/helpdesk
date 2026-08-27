# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import fields, models


class HelpdeskTicketStage(models.Model):
    _inherit = "helpdesk.ticket.stage"

    task_stage_ids = fields.Many2many(
        "project.task.type",
        relation="project_task_type_helpdesk_ticket_stage_rel",
        column1="helpdesk_ticket_stage_id",
        column2="project_task_type_id",
    )
    sync_limit_single_task = fields.Boolean(
        string="Sync Only If Single Task",
        default=False,
        help="If checked, stage synchronization from Project Tasks to Helpdesk Tickets "
        "will only happen if the Ticket is linked to exactly one Task. "
        "If the Ticket has multiple tasks, the stage change will not propagate.",
    )
