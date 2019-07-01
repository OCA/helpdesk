from odoo import fields, models


class HelpdeskTicketTag(models.Model):
    _name = 'helpdesk.ticket.tag'
    _description = 'Helpdesk Ticket Tag'

    name = fields.Char(string='Name')
    color = fields.Integer(string='Color Index')
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        default=lambda self: self.env['res.company']._company_default_get(
            'helpdesk.ticket')
    )
