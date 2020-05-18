from odoo import models, fields, api

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    ticket_id = fields.Many2one(
        comodel_name='helpdesk.ticket',
        string='ticket_id',
    )