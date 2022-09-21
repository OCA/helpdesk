# Copyright 2021 Sirum GmbH
# Copyright 2021 elego Software Solutions GmbH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class HelpdeskSolution(models.Model):
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _name = "helpdesk.solution"
    _description = "Helpdesk Solution"

    title = fields.Char()
    description = fields.Text()
    tag_ids = fields.Many2many(comodel_name="helpdesk.ticket.tag")
    ticket_ids = fields.Many2many(
        comodel_name="helpdesk.ticket",
    )
    ticket_count = fields.Integer(
        compute="_compute_ticket_count",
        store=True,
    )

    @api.depends("ticket_ids")
    def _compute_ticket_count(self):
        for rec in self:
            rec.ticket_count = len(rec.ticket_ids)

    def button_tickets(self):
        self.ensure_one()
        res_action = self.env["ir.actions.act_window"]._for_xml_id(
            "helpdesk_mgmt.helpdesk_ticket_action"
        )
        res_domain = res_action.get("domain") or []
        if type(res_domain) == str:
            res_domain = safe_eval(res_domain)
        res_domain.append(("id", "in", self.ticket_ids.ids))
        res_action["domain"] = res_domain
        return res_action
