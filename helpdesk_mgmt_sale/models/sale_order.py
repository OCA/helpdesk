from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    ticket_ids = fields.Many2many("helpdesk.ticket")
    ticket_count = fields.Integer(
        string="Tickets Count", compute="_compute_ticket_count", store=True
    )

    @api.depends("ticket_ids")
    def _compute_ticket_count(self):
        for order in self:
            order.ticket_count = len(order.ticket_ids)

    def action_create_helpdesk_ticket(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Create Helpdesk ticket",
            "res_model": "helpdesk.ticket",
            "view_mode": "form",
            "view_id": self.env.ref("helpdesk_mgmt.ticket_view_form").id,
            "target": "new",
            "context": {
                "default_partner_id": self.partner_id.id,
                "default_name": self.name,
                "default_origin": self.name,
                "default_sale_order_ids": [(4, self.id)],
                "from_sale_order": True,
            },
        }
