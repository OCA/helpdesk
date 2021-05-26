from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

DEFAULT_DAYS = 30


class HelpdeskTicketStage(models.Model):
    _inherit = "helpdesk.ticket.stage"

    auto_stage = fields.Boolean(default=False)
    destination_stage = fields.Many2one("helpdesk.ticket.stage")
    inactivity_time = fields.Integer(
        string="Inactivity time for stage change(Days)",
        default=DEFAULT_DAYS
    )

    @api.onchange('auto_stage')
    def _onchange_auto_stage(self):
        if not self.auto_stage:
            self.destination_stage = False
            self.inactivity_time = False
        else:
            self.inactivity_time = DEFAULT_DAYS

    @api.onchange('destination_stage')
    def _onchange_destination_stage(self):
        if self.auto_stage and self.destination_stage.id == self._origin.id:
            raise ValidationError(_(
                "Wrong value for Destination Stage:"
                " It cannot be the same stage!"
            ))

    @api.onchange('inactivity_time')
    def _onchange_inactivity_time(self):
        if self.auto_stage and self.inactivity_time <= 0:
            raise ValidationError(_(
                "Wrong value for Inactivity Time:"
                " Must be positive!"
            ))
