# Copyright 2019 Georg Notter <georg.notter@agenterp.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    project_id = fields.Many2one(
        comodel_name='project.project',
        string="Project",
    )
    timesheet_ids = fields.One2many(
        comodel_name='account.analytic.line',
        inverse_name='helpdesk_ticket_id',
        string="Timesheet",
    )

    @api.multi
    def write(self, values):
        res = super(HelpdeskTicket, self).write(values)
        if values.get('stage_id'):
            if self.stage_id.timesheet_required:
                if len(self.timesheet_ids) == 0:
                    raise ValidationError(
                        _("Timesheet Required: "
                            "Please provide a Timesheet\
                          to reach this ticket stage"))
        return res
