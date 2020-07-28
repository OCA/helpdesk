###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, fields, models


class HelpdeskTicketTeam(models.Model):
    _inherit = 'helpdesk.ticket.team'

    allow_timesheet = fields.Boolean(
        string='Allow Timesheet',
    )
    default_analytic_account = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Default Analytic Account',
    )
    reset_default_analytic_account = fields.Boolean(
        string='Reset Analytic Account',
    )

    @api.constrains('allow_timesheet')
    def _constrains_allow_timesheet(self):
        if not self.allow_timesheet:
            self.default_analytic_account = False

    def action_clear(self):
        self.default_analytic_account = False
