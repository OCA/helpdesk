from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    helpdek_from_email = fields.Char(
        string="From email",
        related="company_id.helpdek_from_email",
        readonly=False,
        help="From Email used when sending helpdesk email from Odoo",
    )
    enable_ticket_idle = fields.Boolean(
        "Auto close idle tickets?",
        related="company_id.enable_ticket_idle",
        readonly=False,
    )
    ticket_idle_period = fields.Integer(
        "Tickets idle for X days",
        related="company_id.ticket_idle_period",
        readonly=False,
        help="Idle period for Ticket. \
        After X days ticket status changed to done automatically.",
    )
    ticket_stage_id = fields.Many2one(
        "helpdesk.ticket.stage",
        string="Stage",
        related="company_id.ticket_stage_id",
        readonly=False,
    )
