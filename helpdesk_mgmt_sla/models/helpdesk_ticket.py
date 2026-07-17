#    Copyright (C) 2020 GARCO Consulting <www.garcoconsulting.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    team_sla = fields.Boolean(string="Team SLA", related="team_id.use_sla")
    ticket_sla_ids = fields.One2many(
        "helpdesk.ticket.sla", inverse_name="ticket_id", readonly=True
    )
    sla_ids = fields.Many2many(
        comodel_name="helpdesk.sla",
        string="Applicable SLAs",
        compute="_compute_sla_ids",
    )
    sla_expired = fields.Boolean(
        string="SLA expired", compute="_compute_sla_data", search="_search_sla_expired"
    )
    sla_deadline = fields.Datetime(string="SLA deadline", compute="_compute_sla_data")
    sla_fits = fields.Boolean(compute="_compute_sla_fits")

    def _compute_sla_fits(self):
        for ticket in self:
            ticket.sla_fits = ticket.sla_ids == ticket._get_sla()

    @api.depends("ticket_sla_ids", "ticket_sla_ids.state", "ticket_sla_ids.deadline")
    def _compute_sla_data(self):
        now = fields.Datetime.now()
        for ticket in self:
            ticket.sla_expired = any(
                ticket.ticket_sla_ids.filtered(
                    lambda sla: sla.state == "expired"
                    or (
                        sla.state == "in_progress"
                        and sla.deadline
                        and sla.deadline < now
                    )
                )
            )
            ticket.sla_deadline = min(
                ticket.ticket_sla_ids.filtered(
                    lambda r: r.state == "in_progress"
                ).mapped("deadline"),
                default=False,
            )

    @api.depends("ticket_sla_ids")
    def _compute_sla_ids(self):
        for ticket in self:
            ticket.sla_ids = ticket.ticket_sla_ids.sla_id

    def _get_sla_ticket_domain(self):
        domain = ["|", ("team_ids", "=", False), ("team_ids", "=", self.team_id.id)]
        if self.tag_ids:
            domain += [
                "|",
                ("tag_ids", "=", False),
                ("tag_ids", "in", self.tag_ids.ids),
            ]
        else:
            domain += [("tag_ids", "=", False)]
        if self.category_id:
            domain += [
                "|",
                ("category_ids", "=", False),
                ("category_ids", "=", self.category_id.id),
            ]
        else:
            domain += [("category_ids", "=", False)]
        return domain

    def _get_sla(self):
        slas = self.env["helpdesk.sla"]
        for sla in self.env["helpdesk.sla"].search(self._get_sla_ticket_domain()):
            if not sla.domain or self.filtered_domain(safe_eval(sla.domain)):
                slas |= sla
        return slas

    def set_sla(self):
        for ticket in self:
            ticket.ticket_sla_ids.unlink()
            if ticket.team_id.use_sla:
                for sla in ticket._get_sla():
                    self.env["helpdesk.ticket.sla"].create(
                        {"ticket_id": ticket.id, "sla_id": sla.id}
                    )

    @api.model_create_multi
    def create(self, vals_list):
        tickets = super().create(vals_list)
        tickets.set_sla()
        return tickets

    def write(self, vals):
        result = super().write(vals)
        if "stage_id" in vals:
            for ticket_sla in self.ticket_sla_ids:
                ticket_sla._stage_recompute()
        return result

    def refresh_sla(self):
        self.ensure_one()
        slas = self._get_sla()
        self.ticket_sla_ids.filtered(lambda r: r.sla_id not in slas).unlink()
        for sla in slas - self.sla_ids:
            self.env["helpdesk.ticket.sla"].create(
                {"ticket_id": self.id, "sla_id": sla.id}
            )

    def _search_sla_expired(self, operator, value):
        return [("ticket_sla_ids.expired", operator, value)]
