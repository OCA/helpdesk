# Copyright (C) 2019 Konos
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class HelpdeskMotive(models.Model):
    _name = "helpdesk.ticket.motive"
    _description = 'Helpdesk Motive'
    _order = "name asc"

    name = fields.Char('Name', required=True)
    team_id = fields.Many2one('helpdesk.ticket.team', string='Helpdesk Team')
