from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    ticket_ids = fields.One2many(
        comodel_name="helpdesk.ticket",
        inverse_name="user_id",
        string="Related tickets",
    )
