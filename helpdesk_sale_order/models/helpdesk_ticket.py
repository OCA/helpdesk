from odoo import _, api, fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    @api.depends("coupon_ids")
    def _compute_coupon_count(self):
        for record in self:
            record.coupon_count = len(record.coupon_ids)

    sale_order_id = fields.Many2one(
        comodel_name="sale.order",
        string="Sale order",
    )

    assign_sale_order = fields.Boolean(
        string="Assign sale order",
        related="team_id.assign_sale_order",
        help="""
        Given a ticket from this team,
        allows assigning a past sale order the customer has
        """,
        invisible=True,
    )

    ticket_return_rel = fields.Boolean(string="Return", related="team_id.ticket_return")

    picking_count = fields.Integer(
        string="Returns",
        compute="_compute_pickings",
        store=True,
        track_visibility="onchange",
    )
    picking_ids = fields.Many2many(
        comodel_name="stock.picking", inverse_name="ticket_id", string="Pickings"
    )

    coupon_ids = fields.One2many(
        string="Coupons", comodel_name="sale.coupon", inverse_name="ticket_id"
    )

    assign_coupon = fields.Boolean(
        string="Coupon",
        default=False,
        related="team_id.assign_coupon",
        help="Allow tickets to assign a coupon",
    )

    coupon_count = fields.Integer(
        string="Coupons", compute=_compute_coupon_count, required=False
    )

    def action_add_coupon(self) -> dict:
        view = self.env.ref("helpdesk_sale_order.sale_coupon_wizard_view_form")
        wiz = self.env["sale.coupon.wizard"].create(
            {
                "ticket_id": self.id,
                "partner_id": self.partner_id.id,
                "sale_order_id": self.sale_order_id.id,
            }
        )

        return {
            "name": _("Add coupon"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "sale.coupon.wizard",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "res_id": wiz.id,
            "context": self.env.context,
        }

    @api.depends("picking_ids")
    def _compute_pickings(self):
        for record in self:
            record.picking_count = len(record.picking_ids)

    def action_create_sales_order(self):
        return {
            "view_type": "form",
            "view_mode": "form",
            "res_model": "create.sales.order.wizard",
            "type": "ir.actions.act_window",
            "target": "new",
            "res_id": False,
            "context": self.env.context,
        }

    def action_view_picking(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Return Orders",
            "view_mode": "tree,form",
            "res_model": "stock.picking",
            "domain": [("id", "in", self.picking_ids.ids)],
            "context": "{'create': False}",
        }

    def action_view_coupon_ids(self):
        return {
            "type": "ir.actions.act_window",
            "name": _("Coupons"),
            "view_mode": "tree,form",
            "res_model": "sale.coupon",
            "domain": [("id", "in", self.coupon_ids.ids)],
        }
