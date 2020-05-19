from odoo import api, fields, models


class ReturnPickingLine(models.TransientModel):
    _inherit = "stock.return.picking.line"


class ReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    related_ticket_id = fields.Many2one(
        comodel_name="helpdesk.ticket", string="Related ticket"
    )

    def create_returns(self):
        picking = super(ReturnPicking, self).create_returns()
        if self.related_ticket_id:
            self.related_ticket_id.picking_ids = [(4, picking["res_id"])]

        return picking
