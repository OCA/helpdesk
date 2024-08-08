from odoo import fields, models


class HelpdeskTicketTeam(models.Model):
    _inherit = "helpdesk.ticket.team"

    is_set_activity = fields.Boolean(
        string="Set Activities",
        help="Available to set activity on source record from ticket",
    )
    activity_stage_id = fields.Many2one(
        comodel_name="helpdesk.ticket.stage",
        string="Done Activity Stage",
        domain="['|', ('team_ids', 'in, []'), ('team_ids', 'in', [id])]",
        help="Move the ticket when the activity in source record is done",
    )
