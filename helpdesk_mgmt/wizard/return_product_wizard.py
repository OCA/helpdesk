from odoo import api, fields, models

class ReturnProductLine(models.TransientModel):
    _name = "return.product.line"
    _description = "Return Product Line"

    return_id = fields.Many2one(
        comodel_name="return.product.wizard", string="Product"
    )
    product_id = fields.Many2one(
        comodel_name="product.product", string="Product", domain="[('id', '=', product_id)]"
    )
    quantity = fields.Float("Quantity", digits='Product Unit of Measure', required=True)
    move_id = fields.Many2one('stock.move', "Move")
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', related='move_id.product_uom', readonly=False)


class ReturnProductWizard(models.TransientModel):
    _name = "return.product.wizard"
    _description = "Return product wizard"

    return_product_id = fields.Many2one(
        comodel_name="stock.picking", string="Product to return", domain="[('picking_type_code', '=', 'outgoing'), ('state', '=', 'done')]"
    )

    product_return_lines_ids = fields.One2many(
        comodel_name="return.product.line", inverse_name="return_id", string="Product lines"
    )

    @api.onchange('return_product_id')
    def _onchange_return_product(self):
        self.product_return_lines_ids = False
        lines = []
        for line in self.return_product_id.move_ids_without_package:
            vals = {
                "product_id": line.product_id.id,
                "quantity": line.product_uom_qty
            }
            lines.append((0, 0, vals))
        self.product_return_lines_ids = lines

    def button_return(self):
        self.ensure_one()
        # move_vals = {
        #     "product_id": self.product_id.id,
        #     "product_uom": self.product_id.uom_id,
        #     "product_uom_qty": 1.0,
        # }
        #
        # move_ids = self.env["stock.move"].create(move_vals)

        picking_type = self.env["stock.picking.type"].search([('code', '=', 'incoming')])

        vals = {
            "location_id": self.return_product_id.location_id.id,
            "location_dest_id": self.return_product_id.location_dest_id.id,
            "product_id": self.return_product_id.product_id.id,
            "picking_type_id": picking_type[0].id,
            "ticket_id": self.return_product_id.ticket_id.id,
            "origin": f"Return of {self.return_product_id.name}",
            "partner_id": self.return_product_id.partner_id.id,
            # "move_ids_without_package": [(6, 0, self.product_return_lines_ids.ids)]
        }
        picking = self.env["stock.picking"].create(vals)
        # import pdb; pdb.set_trace()
        return picking
