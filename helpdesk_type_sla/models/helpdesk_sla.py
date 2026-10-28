# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HelpdeskSla(models.Model):
    _inherit = "helpdesk.sla"

    type_ids = fields.Many2many(comodel_name="helpdesk.ticket.type", string="Types")
