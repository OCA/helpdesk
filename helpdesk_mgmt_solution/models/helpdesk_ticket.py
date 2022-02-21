# Copyright 2021 Sirum GmbH
# Copyright 2021 elego Software Solutions GmbH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.tools import safe_eval


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    solution_ids = fields.Many2many(
        comodel_name="helpdesk.solution",
    )

    solution_count = fields.Integer(
        compute="_compute_solution_count",
        store=True,
    )

    @api.depends("solution_ids")
    def _compute_solution_count(self):
        for rec in self:
            rec.solution_count = len(rec.solution_ids)

    def button_solutions(self):
        self.ensure_one()
        action = self.env.ref(
            "helpdesk_mgmt_solution.act_show_helpdesk_ticket_solutions"
        )
        res_action = action.read()[0]
        ctx = {
            "helpdesk_ticket_id": self.id,
        }
        res_domain = res_action.get("domain") or []
        if type(res_domain) == str:
            res_domain = safe_eval(res_domain)
        res_domain.append(("id", "in", self.solution_ids.ids))
        res_action["domain"] = res_domain
        res_ctx = safe_eval(res_action.get("context"))
        res_ctx.update(ctx)
        res_action["context"] = res_ctx
        return res_action

    def button_create_solution(self):
        ctx = {
            "create_solution": True,
            "default_ticket_id": self.id,
            "default_tag_ids": [(4, tag_id) for tag_id in self.tag_ids.ids],
        }
        view_id = self.env.ref(
            "helpdesk_mgmt_solution.view_helpdesk_solution_wizard_form"
        )
        return {
            "res_model": "helpdesk.solution.wizard",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "view_type": "form",
            "view_id": view_id.id,
            "target": "new",
            "context": ctx,
        }

    def button_search_solution(self):
        ctx = {
            "search_solution": True,
            "default_ticket_id": self.id,
            "default_solution_ids": [(6, 0, self.solution_ids.ids)],
            "default_tag_ids": [(4, tag_id) for tag_id in self.tag_ids.ids],
        }
        view_id = self.env.ref(
            "helpdesk_mgmt_solution.view_helpdesk_solution_wizard_form"
        )
        return {
            "res_model": "helpdesk.solution.wizard",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "view_type": "form",
            "view_id": view_id.id,
            "target": "new",
            "context": ctx,
        }
