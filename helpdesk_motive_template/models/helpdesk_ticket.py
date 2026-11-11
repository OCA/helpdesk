# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import is_html_empty


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    description = fields.Html(
        compute="_compute_description",
        store=True,
        readonly=False,
    )

    def _get_motive_rendering_context(self) -> dict:
        self.ensure_one()
        return {
            "model": self._name,
            "res_ids": self.ids or [False],
            "object": self,
            "ticket": self,
        }

    def _render_description_from_template(self, description_template) -> str:
        self.ensure_one()
        if not description_template:
            return ""

        render_context = self._get_motive_rendering_context()

        res_model = render_context.get("model", "helpdesk.ticket")
        res_ids = render_context.get("res_ids", [False])

        rendered_descriptions = self.env[
            "mail.render.mixin"
        ]._render_template_inline_template(
            description_template,
            model=res_model,
            res_ids=res_ids,
            add_context=render_context,
        )
        return rendered_descriptions.get(res_ids[0], "")

    @api.depends("motive_id")
    def _compute_description(self):
        res = None
        # Base helpdesk.ticket does not compute description. Delegate upstream only
        # if another module in the MRO (e.g. helpdesk_mgmt_template) defined it.
        if hasattr(super(), "_compute_description"):
            res = super()._compute_description()
        for ticket in self:
            description_template = ticket.motive_id.description_template
            if ticket.motive_id and not is_html_empty(description_template):
                ticket.description = ticket._render_description_from_template(
                    description_template
                )
        return res
