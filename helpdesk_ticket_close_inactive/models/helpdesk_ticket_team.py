# Copyright 2024 APSL-Nagarro - Miquel Alzanillas
import logging
from datetime import datetime, timedelta

from odoo import fields, models

_logger = logging.getLogger(__name__)


class HelpdeskTicketTeam(models.Model):
    _inherit = "helpdesk.ticket.team"

    def _default_warning_email_template(self):
        try:
            return self.env.ref(
                "helpdesk_ticket_close_inactive.warning_inactive_ticket_template"
            ).id
        except Exception:
            _logger.info("Default warning email template not exists.")

    def _default_closing_email_template(self):
        try:
            return self.env.ref("helpdesk_mgmt.closed_ticket_template").id
        except Exception:
            _logger.info("Default closing email template not exists.")

    close_inactive_tickets = fields.Boolean(
        string="Automatic closure of inactive tickets",
        help="This option enables a cronjob to automatically close inactive tickets.",
        default=False,
    )
    ticket_stage_ids = fields.Many2many(
        comodel_name="helpdesk.ticket.stage",
        string="Ticket Stage",
        help="The cronjob will check for inactivity in tickets that are in these stages.",
    )
    ticket_category_ids = fields.Many2many(
        comodel_name="helpdesk.ticket.category",
        relation="closing_ticket_type_filter",
        string="Ticket Category",
        help="The cronjob will check for inactivity in tickets \
        that belongs to this categories.",
    )
    inactive_tickets_day_limit_warning = fields.Integer(
        default=7,
        string="Inactive days limit before send a warning",
        required=1,
        help="Day limit for email notification of upcoming ticket closure due to inactivity.",
    )
    warning_inactive_mail_template_id = fields.Many2one(
        "mail.template",
        default=_default_warning_email_template,
        string="Inactivity warning email template",
        help="Template to be sent on inactive ticket closing notification",
    )
    inactive_tickets_day_limit_closing = fields.Integer(
        default=14,
        required=1,
        help="Day limit for automatic ticket closing due to inactivity.",
    )
    close_inactive_mail_template_id = fields.Many2one(
        "mail.template",
        default=_default_closing_email_template,
        string="Closing email template",
        help="Template to be sent on inactive ticket closing notification",
    )
    closing_ticket_stage = fields.Many2one(
        "helpdesk.ticket.stage",
        string="Closing Stage",
        help="Set this stage for autoclosing tickets",
    )

    def close_team_inactive_tickets(self):

        if len(self) > 0:
            teams = self
        else:
            teams = self.search([("close_inactive_tickets", "=", True)])

        for team_id in teams:
            ticket_stage_ids = team_id.ticket_stage_ids.ids
            ticket_category_ids = team_id.ticket_category_ids.ids
            warning_limit = datetime.today() - timedelta(
                days=team_id.inactive_tickets_day_limit_warning
            )
            closing_limit = datetime.today() - timedelta(
                days=team_id.inactive_tickets_day_limit_closing
            )
            closing_remaining_days = (
                team_id.inactive_tickets_day_limit_closing
                - team_id.inactive_tickets_day_limit_warning
            )
            closing_stage = team_id.closing_ticket_stage
            warning_ticket_ids = self.env["helpdesk.ticket"].search(
                [
                    ("team_id", "=", team_id.id),
                    ("stage_id", "in", ticket_stage_ids),
                    ("category_id", "in", ticket_category_ids),
                    ("last_stage_update", "<=", warning_limit),
                    ("last_stage_update", ">", closing_limit),
                ]
            )
            warning_email_ids = []
            closing_email_ids = []
            if warning_ticket_ids:
                for ticket in warning_ticket_ids:
                    # Set template context
                    context = {
                        "stage": ticket.stage_id.name,
                        "close": False,
                        "remaining_days": closing_remaining_days,
                    }
                    # Send warning email
                    warning_email_id = (
                        team_id.warning_inactive_mail_template_id.with_context(
                            **context
                        ).send_mail(ticket.id)
                    )
                    if warning_email_id:
                        _logger.info(
                            "Sending warning ticket email for %s", ticket.number
                        )
                        warning_email_ids.append(warning_email_id)

            closing_ticket_ids = self.env["helpdesk.ticket"].search(
                [
                    ("team_id", "=", team_id.id),
                    ("stage_id", "in", ticket_stage_ids),
                    ("category_id", "in", ticket_category_ids),
                    ("last_stage_update", "<=", closing_limit),
                ]
            )
            if closing_ticket_ids:
                for ticket in closing_ticket_ids:
                    context = {"stage": ticket.stage_id.name, "close": True}
                    ticket.write({"stage_id": closing_stage.id})
                    # Send closing email
                    closing_email_id = (
                        team_id.close_inactive_mail_template_id.with_context(
                            **context
                        ).send_mail(ticket.id)
                    )
                    if closing_email_id:
                        _logger.info(
                            "Sending autoclosing ticket email for %s", ticket.number
                        )
                        closing_email_ids.append(closing_email_id)

                        # Log atomated closing ticket action into chatter
                        msg = "Ticket closed automatically because have \
                        reached the inactivity days limit"
                        ticket.message_post(body=msg)
            return {
                "warning_email_ids": warning_email_ids,
                "closing_email_ids": closing_email_ids,
            }
