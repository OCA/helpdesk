from odoo import models, fields


class HelpdeskSalesOrder(models.Model):
    _inherit = "helpdesk.ticket"

    sale_order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Sales order',
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

#    tag_ids = fields.Many2many(
#      comodel_name="product.template.tag",
#        string="Product tags",
#        #relation="product_tag_ids",
#        #column1="kit_line_ids",
#        #column2="tags",
#    )

#    @api.onchange('product_id')
#    def update_product_tags(self):
#        for record in self:
#            record.tag_ids = [(6, 0, record.product_id.tag_ids.ids)]
