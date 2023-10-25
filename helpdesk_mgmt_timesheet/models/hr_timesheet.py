###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    ticket_id = fields.Many2one(
        comodel_name="helpdesk.ticket",
        string="Ticket",
        domain=[("project_id", "!=", False)],
        groups="helpdesk_mgmt.group_helpdesk_user",
    )
    ticket_partner_id = fields.Many2one(
        comodel_name="res.partner",
        related="ticket_id.partner_id",
        string="Ticket partner",
        store=True,
        compute_sudo=True,
        groups="helpdesk_mgmt.group_helpdesk_user",
    )

    @api.onchange("ticket_id")
    def onchange_ticket_id(self):
        for record in self:
            if not record.ticket_id:
                continue
            record.project_id = record.ticket_id.project_id
            record.task_id = record.ticket_id.task_id
