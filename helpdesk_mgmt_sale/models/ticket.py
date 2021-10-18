# Copyright 2021 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    def _get_sale_domain(self):
        res = "[]"
        if not self.partner_id:
            return res
        return "[('partner_id', '=', self.partner_id.id)]"

    sale_id = fields.Many2one(comodel_name="sale.order", domain=_get_sale_domain)
    sale_line_ids = fields.One2many(
        comodel_name="helpdesk.ticket.sale.line", inverse_name="ticket_id"
    )


class HelpdeskTicketSaleLine(models.Model):
    _name = "helpdesk.ticket.sale.line"
    _description = "Sale line linked to the helpdesk ticket"

    def _get_sale_line_domain(self):
        res = "[]"
        if not self.sale_id:
            return res
        return "[('order_id', '=', self.sale_id.id)]"

    ticket_id = fields.Many2one(
        comodel_name="helpdesk.ticket",
        domain=_get_sale_line_domain,
    )
    sale_id = fields.Many2one(
        comodel_name="sale.order", related="ticket_id.sale_id", readonly=True
    )
    sale_line_id = fields.Many2one(comodel_name="sale.order.line", required=True)
    product_id = fields.Many2one(related="sale_line_id.product_id", readonly=True)
    product_name = fields.Char(related="product_id.name", readonly=True)
    qty = fields.Float(string="Quantity", digits="Product Unit of Measure")

    @api.onchange("sale_line_id")
    def onchange_sale_line(self):
        for record in self:
            record.qty = record.sale_line_id.product_uom_qty
