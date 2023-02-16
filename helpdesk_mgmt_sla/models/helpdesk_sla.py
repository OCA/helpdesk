#    Copyright (C) 2020 GARCO Consulting <www.garcoconsulting.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class HelpdeskSla(models.Model):
    _name = "helpdesk.sla"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Helpdesk SLA"

    name = fields.Char(string="Name", required=True)
    team_ids = fields.Many2many(comodel_name="helpdesk.ticket.team", string="Teams")
    category_ids = fields.Many2many(
        comodel_name="helpdesk.ticket.category", string="Categories"
    )
    tag_ids = fields.Many2many(comodel_name="helpdesk.ticket.tag", string="Tags")
    stage_ids = fields.Many2many(comodel_name="helpdesk.ticket.stage", string="Stages")
    days = fields.Integer(string="Days", default=0, required=True)
    hours = fields.Integer(string="Hours", default=0, required=True)
    note = fields.Html(string="Note")
    domain = fields.Char(string="Filter", default="[]")
    active = fields.Boolean(default=True)

    def _default_sla_computation(self):
        return self.env.ref("helpdesk_mgmt.field_helpdesk_ticket__create_date").id

    def _default_sla_expiration(self):
        return self.env.ref("helpdesk_mgmt.field_helpdesk_ticket__closed_date").id

    sla_computation_id = fields.Many2one(
        "ir.model.fields",
        domain="[('model', '=', 'helpdesk.ticket'),('ttype', '=', 'datetime')]",
        default=_default_sla_computation,
    )
    sla_expiration_date = fields.Selection(
        [("current_date", "Current date"), ("fixed_date_field", "Fixed date field")],
        help="This field can take the following values :\n"
        "  * Current date: The SLA will expired at the time of evaluation.\n"
        "  * Fixed date field: You can choose to associate a helpdesk.ticket"
        + "date field with the expiration date of the SLA.",
        default="current_date",
        required=True,
    )
    sla_expiration_id = fields.Many2one(
        "ir.model.fields",
        domain="[('model', '=', 'helpdesk.ticket'),('ttype', '=', 'datetime')]",
        default=_default_sla_expiration,
    )

    def _applies_for(self, ticket):
        self.ensure_one()
        if self.team_ids and ticket.team_id not in self.team_ids:
            return False
        if self.stage_ids and ticket.stage_id not in self.stage_ids:
            return False
        if self.category_ids and ticket.category_id not in self.category_ids:
            return False
        if self.tag_ids and not any(tag in ticket.tag_ids for tag in self.tag_ids):
            return False
        if self.domain and self.domain != "[]":
            domain = safe_eval(self.domain)
            if not ticket.filtered_domain(domain):
                return False
        return True

    @api.model
    def _get_sla_ticket_domain(self):
        return [("stage_id.closed", "=", False)]

    @api.model
    def check_sla(self):
        """Scheduler that checks sla on tickets"""
        tickets = self.env["helpdesk.ticket"].search(self._get_sla_ticket_domain())
        slas = self.search([])
        for ticket in tickets:
            for sla in slas:
                if sla._applies_for(ticket):
                    sla.check_ticket_sla(ticket)
                    break

    def check_ticket_sla(self, tickets):
        self.ensure_one()
        for ticket in tickets:
            deadline = ticket[self.sla_computation_id.name]
            if not deadline:
                continue
            working_calendar = ticket.team_id.resource_calendar_id

            if self.days > 0:
                deadline = working_calendar.plan_days(
                    self.days + 1, deadline, compute_leaves=True
                )
                create_date = ticket[self.sla_computation_id.name]

                deadline = deadline.replace(
                    hour=create_date.hour,
                    minute=create_date.minute,
                    second=create_date.second,
                    microsecond=create_date.microsecond,
                )

                deadline_for_working_cal = working_calendar.plan_hours(0, deadline)

                if (
                    deadline_for_working_cal
                    and deadline.day < deadline_for_working_cal.day
                ):
                    deadline = deadline.replace(
                        hour=0, minute=0, second=0, microsecond=0
                    )

            deadline = working_calendar.plan_hours(
                self.hours, deadline, compute_leaves=True
            )
            ticket.sla_deadline = deadline
            if self.sla_expiration_date == "current_date" or (
                self.sla_expiration_date == "fixed_date_field"
                and not ticket[self.sla_expiration_id.name]
            ):
                if ticket.sla_deadline < datetime.today().now():
                    ticket.sla_expired = True
                else:
                    ticket.sla_expired = False
            if (
                self.sla_expiration_date == "fixed_date_field"
                and ticket[self.sla_expiration_id.name]
            ):
                if ticket.sla_deadline < ticket[self.sla_expiration_id.name]:
                    ticket.sla_expired = True
                else:
                    ticket.sla_expired = False
