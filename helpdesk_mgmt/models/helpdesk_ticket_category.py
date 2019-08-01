from odoo import fields, models


class HelpdeskCategory(models.Model):

    _name = 'helpdesk.ticket.category'
    _description = 'Helpdesk Ticket Category'

    active = fields.Boolean(string='Active', default=True)
    name = fields.Char(string='Name', required=True)
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        default=lambda self: self.env['res.company']._company_default_get(
            'helpdesk.ticket')
    )
