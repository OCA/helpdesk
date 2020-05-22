from odoo import api, fields, models


class ReturnPickingLine(models.TransientModel):
    _inherit = "stock.return.picking.line"


class ReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    related_ticket_id = fields.Many2one(
        comodel_name="helpdesk.ticket", string="Related ticket"
    )

    related_sale_order_id = fields.Many2one(
        comodel_name="sale.order",
        related="related_ticket_id.sale_order_id",
        string="Related sale order",
    )

    def create_returns(self):
        picking = super(ReturnPicking, self).create_returns()
        if self.related_ticket_id:
            self.related_ticket_id.picking_ids = [(4, picking["res_id"])]

        return picking

    @api.onchange("related_sale_order_id")
    def _onchange_picking(self):
        res = [("picking_type_code", "=", "outgoing"), ("state", "=", "done")]
        if self.related_sale_order_id:
            res += [("id", "in", self.related_sale_order_id.picking_ids.ids)]
        return {"domain": {"picking_id": res}}
