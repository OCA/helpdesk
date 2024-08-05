# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    description = fields.Html(
        store=True,
        compute="_compute_description",
        readonly=False,
    )
    helpdesk_ticket_category_ids = fields.Many2many(
        "helpdesk.ticket.category", compute="_compute_helpdesk_ticket_category"
    )

    @api.depends("team_id")
    def _compute_helpdesk_ticket_category(self):
        for rec in self:
            rec.helpdesk_ticket_category_ids = rec.team_id.category_ids

    @api.depends("category_id")
    def _compute_description(self):
        for record in self:
            if record.category_id.template_description:
                record.description = record.category_id.template_description
            elif record.description:
                record.description = record.description
            else:
                record.description = "<p></p>"

    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        if "description" not in default:
            default["description"] = "<p></p>"
        return super().copy(default)
