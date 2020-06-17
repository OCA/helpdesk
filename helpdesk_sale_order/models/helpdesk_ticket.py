from odoo import api, fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    sale_order_id = fields.Many2one(comodel_name="sale.order", string="Sale order",)

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
