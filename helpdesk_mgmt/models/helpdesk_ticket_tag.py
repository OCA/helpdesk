from odoo import api, fields, models


class HelpdeskTicketTag(models.Model):
    _name = 'helpdesk.ticket.tag'
    _description = 'Helpdesk Ticket Tag'

    name = fields.Char(string='Name')
    color = fields.Integer(string='Color Index')
