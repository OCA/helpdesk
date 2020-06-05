# Copyright (C) 2019 Konos
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class HelpdeskType(models.Model):
    """Helpdesk Type"""

    _name = "helpdesk.ticket.type"
    _description = "Helpdesk Ticket Type"
    _order = "name asc"

    name = fields.Char("Name", required=True)
    team_ids = fields.Many2many(
        "helpdesk.ticket.team",
        string="Teams",
        help="Helpdesk teams allowed to use this type.",
    )
