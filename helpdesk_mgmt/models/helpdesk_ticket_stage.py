from datetime import datetime

from odoo import api, fields, models


class HelpdeskTicketStage(models.Model):
    _name = "helpdesk.ticket.stage"
    _description = "Helpdesk Ticket Stage"
    _order = "sequence, id"

    name = fields.Char(string="Stage Name", required=True, translate=True)
    description = fields.Text(translate=True)
    sequence = fields.Integer(default=1)
    active = fields.Boolean(default=True)
    unattended = fields.Boolean(string="Unattended")
    closed = fields.Boolean(string="Closed")
    auto_next_stage_id = fields.Many2one(
        comodel_name=_name, string="Next automatic stage"
    )
    auto_next_number = fields.Integer(
        string="Next automatic date number",
        help="Numbers which are not multiple of ten are not advised,"
        " since the automatic check is done hourly",
    )
    auto_next_type = fields.Selection(
        string="Next automatic date type",
        selection=[("hour", "Hours"), ("day", "Days"), ("week", "Weeks")],
    )

    mail_template_id = fields.Many2one(
        comodel_name="mail.template",
        string="Email Template",
        domain=[("model", "=", "helpdesk.ticket")],
        help="If set an email will be sent to the "
        "customer when the ticket"
        "reaches this step.",
    )
    fold = fields.Boolean(
        string="Folded in Kanban",
        help="This stage is folded in the kanban view "
        "when there are no records in that stage "
        "to display.",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )

    ticket_ids = fields.One2many(
        comodel_name="helpdesk.ticket",
        inverse_name="stage_id",
        string="Tickets",
    )

    # called by cron
    @api.model
    def change_stage(self):
        for stage_id in self.env[self._name].search([]):
            if (
                stage_id.auto_next_number
                and stage_id.auto_next_type
                and stage_id.auto_next_stage_id
            ):
                for ticket_id in stage_id.ticket_ids.filtered(
                    lambda x: datetime.now() > x.ticket_change
                ):
                    ticket_id.stage_id = stage_id.auto_next_stage_id.id
                    ticket_id.auto_last_update = datetime.now()
