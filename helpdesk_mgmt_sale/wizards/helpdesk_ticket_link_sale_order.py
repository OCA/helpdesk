from odoo import Command, fields, models


class HelpdeskTicketLinkSaleOrderWizard(models.TransientModel):
    _name = "helpdesk.ticket.link.sale.order.wizard"
    _description = "Link Sale Orders to Helpdesk Ticket"

    ticket_id = fields.Many2one("helpdesk.ticket", required=True, readonly=True)
    ticket_sale_order_ids = fields.Many2many(
        "sale.order", related="ticket_id.sale_order_ids", readonly=True
    )
    commercial_partner_id = fields.Many2one("res.partner", readonly=True)
    sale_orders_ids = fields.Many2many(
        "sale.order",
        domain="["
        "   ('partner_id.commercial_partner_id', '=', commercial_partner_id),"
        "   ('id', 'not in', ticket_sale_order_ids)"
        "]",
        required=True,
    )

    def action_confirm(self):
        self.ensure_one()
        if self.sale_orders_ids:
            self.ticket_id.sale_order_ids = [
                Command.link(so.id) for so in self.sale_orders_ids
            ]
