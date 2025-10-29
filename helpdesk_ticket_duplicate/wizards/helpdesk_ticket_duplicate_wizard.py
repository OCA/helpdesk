from odoo import fields, models
from odoo.exceptions import UserError


class helpdeskTicketDuplicateWizard(models.TransientModel):
    _name = "helpdesk.ticket.duplicate.wizard"
    _description = "helpdesk Ticket Duplicate Wizard"

    ticket_id = fields.Many2one("helpdesk.ticket", required=True)
    duplicate_of_id = fields.Many2one("helpdesk.ticket", required=True)
    target_stage_id = fields.Many2one("helpdesk.ticket.stage", required=True)

    def action_confirm(self):
        if not self.duplicate_of_id:
            raise UserError(self.env._("You need to set a duplicate!"))
        self.ticket_id.write(
            {
                "duplicate_id": self.duplicate_of_id.id,
                "stage_id": self.target_stage_id.id,
            }
        )
