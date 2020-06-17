from odoo import _, fields, models


class SaleCouponWizard(models.TransientModel):
    _name = "sale.coupon.wizard"
    _description = "Add new sale coupon wizard"

    name = fields.Char(string="Name")

    ticket_id = fields.Many2one(
        comodel_name="helpdesk.ticket", string="Ticket", required=True
    )

    partner_id = fields.Many2one(
        comodel_name="res.partner", string="Partner", required=True
    )

    sale_order_id = fields.Many2one(
        comodel_name="sale.order", string="Order reference", required=True
    )

    program_id = fields.Many2one(
        comodel_name="sale.coupon.program",
        string="Coupon program",
        domain=lambda self: [("program_type", "=", "coupon_program")],
    )

    def action_create_coupon(self):
        coupon_id = self.env["sale.coupon"].create(
            {
                "program_id": self.program_id.id,
                "order_id": self.sale_order_id.id,
                "partner_id": self.partner_id.id,
            }
        )
        if self.program_id and self.sale_order_id and self.partner_id:
            self.ticket_id.coupon_ids = [(4, coupon_id.id)]
            return {
                "name": _("Coupon %s" % coupon_id.code),
                "type": "ir.actions.act_window",
                "res_model": "sale.coupon",
                "res_id": coupon_id.id,
                "view_mode": "form",
            }
