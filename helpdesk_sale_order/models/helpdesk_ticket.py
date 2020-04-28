from odoo import models, fields


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    sale_order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Sale order',
        domain='[("partner_id", "=", "partner_id.sale_order_ids.ids")]',
    )

    assign_sale_order = fields.Boolean(
        string="Assign sale order",
        related="team_id.assign_sale_order",
        help="""
        Given a ticket from this team, allows assigning a past sale order the customer has
        """,
        invisible=True
    )

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
