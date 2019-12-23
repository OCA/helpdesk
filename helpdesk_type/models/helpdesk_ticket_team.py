# Copyright (c) 2019 Open Source Integrators
# Copyright (C) 2019 Konos
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class HelpdeskTeam(models.Model):
    _inherit = 'helpdesk.ticket.team'

    type_ids = fields.Many2many(
        'helpdesk.ticket.type',
        string='Ticket Type',
        help="Ticket Types the team will use. This team's tickets will only "
             "be able to use those types.")
