from odoo import api, fields, models

class HelpdeskCategory(models.Model):

    _name = 'helpdesk.ticket.category'

    active = fields.Boolean(string='Active')
    name = fields.Char(string='Name', required=True)


