from odoo import models


class HeldpdeskSalesOrderWizard(models.TransientModel):
    _name = "helpdesk.sales.order.wizard"
    _description = "Create sales orders from tickets"

#    close_reason_id = fields.Many2one(
#        comodel_name="sale.subscription.close.reason", string="Reason"
#    )

#    @api.one
#    def button_create_sales_order(self):
#        sale_subscription_id = self.env["sale.subscription"].search(
#            [("id", "=", self.env.context["active_id"])]
#        )
#        sale_subscription_id.close_reason_id = self.close_reason_id.id
#        stage = sale_subscription_id.stage_id
#        closed_stage = self.env["sale.subscription.stage"].search(
#            [("type", "=", "post")]
#        )
#        if stage != closed_stage:
#            sale_subscription_id.stage_id = closed_stage
#            sale_subscription_id.close_reason_id = self.close_reason_id.id
#            sale_subscription_id.active = False
