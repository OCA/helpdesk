# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv.expression import TRUE_DOMAIN


class StockHelpdeskTicketCreate(models.TransientModel):
    _name = "stock.helpdesk.ticket.create"
    _description = "Wizard to create Heldpesk ticket in stock"

    description = fields.Char()
    stock_move_id_domain = fields.Binary(compute="_compute_stock_move_id_domain")
    stock_move_id = fields.Many2one(
        comodel_name="stock.move",
        compute="_compute_stock_move_id",
        readonly=False,
        store=True,
        precompute=True,
        ondelete="cascade",
    )
    stock_picking_id = fields.Many2one(
        comodel_name="stock.picking",
        compute="_compute_stock_picking_id",
        readonly=False,
        store=True,
        precompute=True,
        ondelete="cascade",
    )
    motive_id = fields.Many2one("helpdesk.ticket.motive")

    def _prepare_ticket_values(self) -> dict:
        """
        Prepare the helpdesk ticket values for creation
        """
        values = {
            "name": self.description,
            "description": self.description,
            "partner_id": self.stock_picking_id.partner_id.id,
            "stock_picking_id": self.stock_picking_id.id,
            "stock_move_id": self.stock_move_id.id,
            "product_id": self.stock_move_id.product_id.id,
            "team_id": self.stock_picking_id.picking_type_id.default_helpdesk_team_id.id,
            "motive_id": self.motive_id.id,
        }
        return values

    def _check_ticket_creation_allowed(self):
        for wizard in self:
            if not wizard.stock_picking_id.helpdesk_ticket_allowed:
                raise ValidationError(
                    _(
                        "You are not allowed to create an helpdesk ticket"
                        " for that operation type! Please call your administrator."
                    )
                )

    def action_create_helpdesk_ticket(self) -> dict:
        self._check_ticket_creation_allowed()
        ticket_values = self._prepare_ticket_values()
        ticket = self.env["helpdesk.ticket"].create(ticket_values)
        action = self.env["ir.actions.actions"]._for_xml_id(
            "helpdesk_mgmt.helpdesk_ticket_action"
        )
        action["domain"] = [("id", "=", ticket.id)]
        return action

    @api.depends()
    def _compute_stock_move_id(self):
        if self.env.context.get("active_model") == "stock.move":
            self.stock_move_id = self.env["stock.move"].browse(
                self.env.context.get("active_id")
            )
        else:
            self.stock_move_id = False

    @api.depends("stock_move_id")
    def _compute_stock_picking_id(self):
        if self.env.context.get("active_model") == "stock.picking":
            self.stock_picking_id = self.env["stock.picking"].browse(
                self.env.context.get("active_id")
            )
        else:
            self.stock_picking_id = False
        for wizard in self:
            if wizard.stock_move_id:
                wizard.stock_picking_id = wizard.stock_move_id.picking_id

    @api.depends("stock_picking_id")
    def _compute_stock_move_id_domain(self):
        picking_records = self.filtered("stock_picking_id")
        without_picking_records = self - picking_records
        for ticket in picking_records:
            if ticket.stock_picking_id:
                ticket.stock_move_id_domain = [
                    ("picking_id", "=", ticket.stock_picking_id.id)
                ]
        if without_picking_records:
            without_picking_records.stock_move_id_domain = TRUE_DOMAIN
