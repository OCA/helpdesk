from odoo import fields, models


class HelpdeskCategory(models.Model):

    _name = "helpdesk.ticket.category"
    _description = "Helpdesk Ticket Category"
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    name = fields.Char(
        string="Name",
        required=True,
        translate=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    default_team_id = fields.Many2one(
        comodel_name="helpdesk.ticket.team",
        string="Default team",
    )
