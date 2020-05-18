from odoo import models, fields, api

class HelpdeskTicketTeam(models.Model):
    _inherit = 'helpdesk.ticket.team'

    archive = fields.Boolean('Archive', related='active', default=True, store=True, readonly=False)    
    
    allow_timesheet = fields.Boolean(
        string="Allow Timesheet",
    )
    default_project = fields.Many2one(
        comodel_name='project.project',
        string='Default Project',
    )

    reset_default_project = fields.Boolean(
        string="Reset Project",
    )

    @api.constrains('allow_timesheet')
    def _constrains_allow_timesheet(self):
        if self.allow_timesheet == False:
            self.default_project = False    
    
    def action_clear(self):
        self.default_project = False    