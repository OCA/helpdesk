# Copyright 2019 Georg Notter <georg.notter@agenterp.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    helpdesk_ticket_id = fields.Many2one(
        comodel_name='helpdesk.ticket',
        string='Helpdesk Ticket',
    )

    @api.onchange('helpdesk_ticket_id')
    def _onchange_helpdesk_ticket_id(self):
        if self.helpdesk_ticket_id.project_id:
            self.project_id = self.helpdesk_ticket_id.project_id.id
