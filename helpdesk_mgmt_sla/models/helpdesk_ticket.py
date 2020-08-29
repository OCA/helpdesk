#    Copyright (C) 2020 GARCO Consulting <www.garcoconsulting.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError
from datetime import timedelta, datetime


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    sla_expired = fields.Boolean(string='SLA expired')
    sla_deadline = fields.Datetime(string='SLA deadline')
