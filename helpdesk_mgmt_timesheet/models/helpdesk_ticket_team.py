###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, fields, models


class HelpdeskTicketTeam(models.Model):
    _inherit = "helpdesk.ticket.team"

    allow_timesheet = fields.Boolean()

    @api.constrains("allow_timesheet")
    def _constrains_allow_timesheet(self):
        if not self.allow_timesheet:
            self.default_project_id = False
