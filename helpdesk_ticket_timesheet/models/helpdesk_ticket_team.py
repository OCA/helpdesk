from odoo import models, fields, api

class HelpdeskTicketTeam(models.Model):
    _inherit = 'helpdesk.ticket.team'

    archive = fields.Boolean('Archive', related='active', default=True, store=True, readonly=False)

    allow_timesheet = fields.Boolean(
        string="Allow Timesheet",
    )
    default_analytic_account = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Default Analytic Account',
    )

    reset_default_analytic_account = fields.Boolean(
        string="Reset Analytic Account",
    )

    @api.constrains('allow_timesheet')
    def _constrains_allow_timesheet(self):
        if self.allow_timesheet == False:
            self.default_analytic_account = False

    def action_clear(self):
        self.default_analytic_account = False
