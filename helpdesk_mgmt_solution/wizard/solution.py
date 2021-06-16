# Copyright 2021 Sirum GmbH
# Copyright 2021 elego Software Solutions GmbH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, fields, models, exceptions
from odoo.tools import safe_eval


class SolutionWizard(models.TransientModel):
    _name = "helpdesk.solution.wizard"

    ticket_id = fields.Many2one(comodel_name="helpdesk.ticket")
    title = fields.Char()
    description = fields.Text()
    tag_ids = fields.Many2many(comodel_name="helpdesk.ticket.tag")
    solution_ids = fields.Many2many(comodel_name="helpdesk.solution")
    hide_solutions = fields.Boolean(
        default=True,
        help="Hide solutions of the current ticket",
    )

    def search_solution(self):
        self.ensure_one()
        action = self.env.ref(
            "helpdesk_mgmt_solution.act_search_helpdesk_solution"
        )
        res_action = action.read()[0]
        ctx = {
            "helpdesk_ticket_id": self.ticket_id.id,
        }
        if self.title:
            ctx["search_default_title"] = self.title
        if self.description:
            ctx["search_default_description"] = self.description
        if self.tag_ids:
            ctx["search_default_tag_ids"] = self.tag_ids.ids

        if self.hide_solutions:
            res_domain = res_action.get("domain") or []
            if type(res_domain) == str:
                res_domain = safe_eval(res_domain)
            res_domain.append(("id", "not in", self.solution_ids.ids))
            res_action["domain"] = res_domain

        res_ctx = safe_eval(res_action.get("context"))
        res_ctx.update(ctx)
        res_action["context"] = res_ctx
        return res_action

    def _prepare_solution_values(self):
        self.ensure_one()
        res = {
            "title": self.title,
            "description": self.description,
            "tag_ids": [(6, 0, self.tag_ids.ids)],
        }
        return res

    def create_solution(self):
        self.ensure_one()
        solution_id = self.env["helpdesk.solution"].create(
            self._prepare_solution_values()
        )
        self.ticket_id.solution_ids = [(4, solution_id.id)]

    def add_solution_to_ticket(self):
        self.ensure_one()
        if self.ticket_id:
            self.ticket_id.solution_ids = [
                (4, solution_id) for solution_id in self.solution_ids.ids
            ]
        else:
            raise exceptions.UserError(_("You have to select a Ticket."))

    def remove_solution_from_ticket(self):
        self.ensure_one()
        if self.ticket_id:
            self.ticket_id.solution_ids = [
                (3, solution_id) for solution_id in self.solution_ids.ids
            ]
        else:
            raise exceptions.UserError(_("You have to select a Ticket."))
