# Copyright 2021 Sirum GmbH
# Copyright 2021 elego Software Solutions GmbH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class HelpdeskSolution(models.Model):
    _name = "helpdesk.solution"

    title = fields.Char()
    description = fields.Text()
    tag_ids = fields.Many2many(comodel_name="helpdesk.ticket.tag")
