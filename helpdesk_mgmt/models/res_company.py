from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    helpdek_from_email = fields.Char(
        "From email",
        help="From Email used when sending helpdesk email from Odoo",
        default="Nitrokey <reply@nitrokey.com>",
    )
    ticket_idle_period = fields.Integer(
        "Tickets idle for X days",
        default=30,
        help="Idle period for Ticket. \
        After X days ticket status changed to done automatically.",
    )
    ticket_stage_id = fields.Many2one("helpdesk.ticket.stage", "Stage")
    enable_ticket_idle = fields.Boolean("Auto close idle tickets?")
    ceo = fields.Char("CEO")

    @api.model
    def format_tz_report(self, dt, tz, date_format=False):

        if not date_format:
            lang = self.env.context.get("lang") or self.env.user.lang
            langs = self.env["res.lang"].search([("code", "=", lang)], limit=1)
            date_format = langs.date_format or "%m-%d-%Y"

        return dt.strftime(date_format)
