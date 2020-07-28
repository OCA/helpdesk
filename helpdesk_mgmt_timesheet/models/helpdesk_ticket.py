###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, fields, models


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    allow_timesheet = fields.Boolean(
        string='Allow Timesheet',
        related='team_id.allow_timesheet',
    )
    planned_hours = fields.Float(
        string='Planned Hours',
        track_visibility='onchange',
    )
    progress = fields.Float(
        compute='_compute_progress_hours',
        group_operator='avg',
        store=True,
        string='Progress',
    )
    remaining_hours = fields.Float(
        compute='_compute_progress_hours',
        readonly=True,
        store=True,
        string='Remaining Hours',
    )
    timesheet_ids = fields.One2many(
        comodel_name='account.analytic.line',
        inverse_name='ticket_id',
        string='Timesheet',
    )
    total_hours = fields.Float(
        compute='_compute_total_hours',
        readonly=True,
        store=True,
        string='Total Hours'
    )

    @api.depends('timesheet_ids.unit_amount')
    def _compute_total_hours(self):
        for record in self:
            record.total_hours = sum(
                record.timesheet_ids.mapped('unit_amount')
            )

    @api.constrains('project_id')
    def _constrains_project_timesheets(self):
        for record in self:
            record.timesheet_ids.update({
                'project_id': record.project_id.id
            })

    @api.onchange('team_id')
    def _onchange_team_id(self):
        for record in self:
            record.project_id = record.team_id.default_project_id

    @api.depends('planned_hours', 'total_hours')
    def _compute_progress_hours(self):
        for ticket in self:
            ticket.progress = 0.0
            if (ticket.planned_hours > 0.0):
                if ticket.total_hours > ticket.planned_hours:
                    ticket.progress = 100
                else:
                    ticket.progress = round(
                        100.0 * ticket.total_hours / ticket.planned_hours,
                        2
                    )
            ticket.remaining_hours = ticket.planned_hours - ticket.total_hours
