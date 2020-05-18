from odoo import models, fields, api

class TicketTimesheet(models.Model):
    _inherit = 'helpdesk.ticket'

    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Analityc Account'
    )

    timesheet_ids = fields.One2many(
        comodel_name='account.analytic.line',
        inverse_name='ticket_id',
        string='Timesheet',
    )
    total_hours = fields.Float(
        compute='impute_hours',
    )

    allow_timesheet = fields.Boolean(
        string="Allow Timesheet",
        related='team_id.allow_timesheet',
    )

    @api.depends('timesheet_ids.unit_amount')
    def impute_hours(self):
        for record in self:
            record.total_hours = sum(record.timesheet_ids.mapped('unit_amount'))

    @api.constrains('analytic_account_id')
    def _constrains_account_timesheets(self):
        for record in self:
            record.timesheet_ids.update({'account_id': record.analytic_account_id.id})

    @api.onchange('team_id')
    def _onchange_team_id(self):
        for record in self:
            record.analytic_account_id = record.team_id.default_analytic_account