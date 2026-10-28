from odoo import fields, models
from odoo.exceptions import UserError


class helpdeskTicketDuplicateWizard(models.TransientModel):
    _name = "helpdesk.ticket.duplicate.wizard"
    _description = "helpdesk Ticket Duplicate Wizard"

    ticket_id = fields.Many2one("helpdesk.ticket", required=True)
    duplicate_of_id = fields.Many2one("helpdesk.ticket", required=True)
    target_stage_id = fields.Many2one("helpdesk.ticket.stage")

    def action_confirm(self):
        if (
            not self.duplicate_of_id
            or self.ticket_id == self.duplicate_of_id
            or self.duplicate_of_id.duplicate_id
        ):
            raise UserError(self.env._("You need to set a valid duplicate!"))
        self.ticket_id.duplicate_id = (self.duplicate_of_id.id,)
        if self.target_stage_id:
            self.ticket_id.stage_id = (self.target_stage_id.id,)
