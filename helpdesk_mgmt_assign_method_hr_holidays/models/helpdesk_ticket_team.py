from odoo import fields, models


class HelpdeskTicketTeam(models.Model):
    _inherit = "helpdesk.ticket.team"

    assign_tickets_to_users_on_leave = fields.Boolean(
        string="Assign tickets to users on leave",
        help="If checked, users with a validated leave covering the current day "
        "can still be auto-assigned to tickets.",
    )

    def _get_available_users(self):
        res = super()._get_available_users()
        if not res or self.assign_tickets_to_users_on_leave:
            return res
        return res.filtered_domain([("is_absent", "!=", True)])
