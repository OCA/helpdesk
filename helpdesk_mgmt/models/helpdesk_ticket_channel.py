from odoo import fields, models


class HelpdeskTicketChannel(models.Model):

    _name = "helpdesk.ticket.channel"
    _description = "Helpdesk Ticket Channel"
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
