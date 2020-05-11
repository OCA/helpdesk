from odoo import api, fields, models

class ReturnProductWizard(models.TransientModel):
    _name = "return.product.wizard"
    _description = "Return product wizard"

    return_product_id = fields.Many2one(
        comodel_name="stock.picking", string="Product to return"
    )

    def button_return(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "stock.picking",
            "view_type": "form",
            "view_mode": "form",
            "view_id": self.env.ref("stock.view_picking_form"),
            "target": "new",
        }
