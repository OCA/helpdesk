# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.osv import expression
from odoo.tools.misc import unquote


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    def _domain_sale_line_id(self):
        domain = expression.AND(
            [
                self.env["sale.order.line"]._sellable_lines_domain(),
                self.env["sale.order.line"]._domain_sale_line_service(),
                [
                    "|",
                    (
                        "order_partner_id.commercial_partner_id.id",
                        "parent_of",
                        unquote("partner_id if partner_id else []"),
                    ),
                    ("order_partner_id", "=?", unquote("partner_id")),
                ],
            ]
        )
        return domain

    sale_order_id = fields.Many2one(
        "sale.order",
        "Sales Order",
        compute="_compute_sale_order_id",
        store=True,
        help="Sales order to which the task is linked.",
        group_expand="_group_expand_sales_order",
    )
    sale_line_id = fields.Many2one(
        "sale.order.line",
        "Sales Order Item",
        copy=True,
        tracking=True,
        index="btree_not_null",
        recursive=True,
        compute="_compute_sale_line",
        store=True,
        readonly=False,
        domain=lambda self: str(self._domain_sale_line_id()),
        help="Sales Order Item to which the time spent on this task will "
        "be added in order to be invoiced to your customer.\n"
        "By default the sales order item set on the project will be selected. "
        "In the absence of one, the last prepaid sales order item that has "
        "time remaining will be used.\n"
        "Remove the sales order item in order to make this task non billable. "
        "You can also change or remove the sales order item of each timesheet "
        "entry individually.",
    )
    allow_billable = fields.Boolean(related="project_id.allow_billable")

    @api.depends(
        "sale_line_id.order_partner_id",
        "task_id.sale_line_id",
        "project_id.sale_line_id",
        "milestone_id.sale_line_id",
        "allow_billable",
    )
    def _compute_sale_line(self):
        for ticket in self:
            if not (ticket.allow_billable or ticket.task_id.allow_billable):
                ticket.sale_line_id = False
                continue
            if not ticket.sale_line_id:
                sale_line = False
                if (
                    ticket.task_id.sale_line_id
                    and ticket.task_id.partner_id.commercial_partner_id
                    == ticket.partner_id.commercial_partner_id
                ):
                    sale_line = ticket.task_id.sale_line_id
                elif ticket.milestone_id.sale_line_id:
                    sale_line = ticket.milestone_id.sale_line_id
                elif (
                    ticket.project_id.sale_line_id
                    and ticket.project_id.partner_id.commercial_partner_id
                    == ticket.partner_id.commercial_partner_id
                ):
                    sale_line = ticket.project_id.sale_line_id
                ticket.sale_line_id = sale_line

    @api.depends("sale_line_id", "project_id", "allow_billable")
    def _compute_sale_order_id(self):
        for ticket in self:
            if not ticket.allow_billable:
                ticket.sale_order_id = False
                continue
            sale_order = (
                ticket.sale_line_id.order_id
                or ticket.project_id.sale_order_id
                or ticket.sale_order_id
            )
            if sale_order and not ticket.partner_id:
                ticket.partner_id = sale_order.partner_id
            consistent_partners = (
                sale_order.partner_id
                | sale_order.partner_invoice_id
                | sale_order.partner_shipping_id
            ).commercial_partner_id
            if ticket.partner_id.commercial_partner_id in consistent_partners:
                ticket.sale_order_id = sale_order
            else:
                ticket.sale_order_id = False
