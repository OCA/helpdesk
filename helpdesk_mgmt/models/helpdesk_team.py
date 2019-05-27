from odoo import api, fields, models


class HelpdeskTeam(models.Model):

    _name = 'helpdesk.ticket.team'
    _description = 'Helpdesk Ticket Team'

    name = fields.Char(string='Name', required=True)
    user_ids = fields.Many2many(comodel_name='res.users', string='Members')
    category_ids = fields.Many2many(comodel_name='helpdesk.ticket.category', string='Category')


