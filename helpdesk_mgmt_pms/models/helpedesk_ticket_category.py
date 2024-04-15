# Copyright (C) 2024 Irlui Ramírez <iramirez.spain@gmail.com>
# Copyright (C) 2024 Consultores Hoteleros Integrales <www.aldahotels.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class HelpdeskCategory(models.Model):

    _inherit = "helpdesk.ticket.category"

    company_ids = fields.Many2many(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
