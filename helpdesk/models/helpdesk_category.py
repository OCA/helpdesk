from odoo import api, fields, models

class HelpdeskCategory(models.Model):

    _name = 'helpdesk.ticket.category'
    _description = 'Helpdesk Ticket Category'

    active = fields.Boolean(string='Active')
    name = fields.Char(string='Name', required=True)


