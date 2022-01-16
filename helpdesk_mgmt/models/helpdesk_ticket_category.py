from odoo import fields, models


class HelpdeskCategory(models.Model):

    _name = "helpdesk.ticket.category"
    _description = "Helpdesk Ticket Category"

    active = fields.Boolean(
        default=True,
    )
    name = fields.Char(
        required=True,
        translate=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
