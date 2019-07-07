# Copyright 2019 Agent ERP GmbH
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class HelpdeskTicketStage(models.Model):
    _inherit = "helpdesk.ticket.stage"

    timesheet_required = fields.Boolean(
        'Timesheet Required', help='To reach this stage,\
        the ticket has to have a timesheet')
