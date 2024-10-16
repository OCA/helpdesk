from odoo import api, fields, models


class MailActivity(models.Model):
    _inherit = "mail.activity"

    ticket_id = fields.Many2one(
        comodel_name="helpdesk.ticket",
        help="Activity created from helpdesk ticket"
        "After closing this activity, ticket is moved to done stage",
    )

    def _action_done(self, feedback=False, attachment_ids=None):
        # Get closed stage for ticket
        for ticket in self.ticket_id:
            if ticket.team_id and ticket.team_id.activity_stage_id:
                # Change ticket stage
                ticket.stage_id = ticket.team_id.activity_stage_id.id
        return super()._action_done(feedback, attachment_ids)

    @api.onchange("activity_type_id")
    def _onchange_activity_type_id(self):
        result = super()._onchange_activity_type_id()
        if self.ticket_id:
            # Add ticket description to action note
            self.note = (self.note or "") + "<br />{}".format(
                self.ticket_id.description
            )
        return result

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        # Set next stage for helpdesk ticket's
        records.ticket_id.set_next_stage()
        return records
