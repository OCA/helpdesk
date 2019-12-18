# Copyright (c) 2019 Open Source Integrators
# Copyright (C) 2019 Konos
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    type_id = fields.Many2one("helpdesk.type", string="Type")
