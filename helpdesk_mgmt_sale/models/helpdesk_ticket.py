# Copyright 2022 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    sale_ids = fields.One2many(
        string="Sale Orders",
        comodel_name="sale.order",
        inverse_name="helpdesk_ticket_id",
        help="Linked Sale Orders to the current Ticket",
    )
    sale_count = fields.Integer("Sale Orders number", compute="_compute_sale_count")

    @api.depends("sale_ids")
    def _compute_sale_count(self):
        for rec in self:
            rec.sale_count = len(rec.sale_ids)

    def action_view_sale_order(self):
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        action["domain"] = [("id", "in", self.sale_ids.ids)]
        action["context"] = {
            "default_helpdesk_ticket_id": self.id,
        }
        if len(self.sale_ids) == 1:
            action["views"] = [(self.env.ref("sale.view_order_form").id, "form")]
            action["res_id"] = self.sale_ids.id
        return action
