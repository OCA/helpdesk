# Copyright (C) 2024 Irlui Ramírez <iramirez.spain@gmail.com>
# Copyright (C) 2024 Consultores Hoteleros Integrales <www.aldahotels.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class HelpdeskCategory(models.Model):

    _inherit = "helpdesk.ticket.category"

    # Sobrescribe el campo company_id cambiándolo a Many2many
    company_ids = fields.Many2many(
        comodel_name="res.company",
        relation="helpdesk_ticket_category_company_rel",
        column1="category_id",
        column2="company_id",
        string="Company",
    )
