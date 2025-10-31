# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import ValidationError
from odoo.fields import Command

from odoo.addons.base.tests.common import BaseCommon


class HelpdeskStockTest(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.PickingType = cls.env["stock.picking.type"]
        cls.suppliers = cls.env.ref("stock.stock_location_suppliers")
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.Product = cls.env["product.product"]
        cls.purchase_team = cls.env["helpdesk.ticket.team"].create(
            {"name": "Purchase Helpdesk"}
        )
        cls.product = cls.Product.create(
            {
                "name": "Product Test",
                "type": "product",
            }
        )
        cls.product_2 = cls.Product.create(
            {
                "name": "Product Test 2",
                "type": "product",
            }
        )
        cls.type_rec = cls.PickingType.create(
            {
                "name": "Reception Test",
                "sequence_code": "REC-TEST",
                "allow_helpdesk_ticket": True,
                "default_helpdesk_team_id": cls.purchase_team.id,
            }
        )

    @classmethod
    def _create_picking(cls):
        cls.picking = cls.env["stock.picking"].create(
            {
                "location_id": cls.suppliers.id,
                "location_dest_id": cls.warehouse.lot_stock_id.id,
                "picking_type_id": cls.type_rec.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "location_id": cls.suppliers.id,
                            "location_dest_id": cls.warehouse.lot_stock_id.id,
                            "product_uom": cls.product.uom_id.id,
                            "product_uom_qty": 10.0,
                        }
                    ),
                    Command.create(
                        {
                            "name": cls.product_2.name,
                            "product_id": cls.product_2.id,
                            "location_id": cls.suppliers.id,
                            "location_dest_id": cls.warehouse.lot_stock_id.id,
                            "product_uom": cls.product_2.uom_id.id,
                            "product_uom_qty": 5.0,
                        }
                    ),
                ],
            }
        )

    def test_helpdesk_creation(self):
        """
        Create a reception stock picking
        Declare an helpdesk ticket on stock move
        Check a ticket is created with corresponding values
        """
        self._create_picking()
        move_p1 = self.picking.move_ids.filtered(
            lambda move: move.product_id == self.product
        )
        wizard = (
            self.env["stock.helpdesk.ticket.create"]
            .with_context(active_model="stock.move", active_id=move_p1.id)
            .create({})
        )
        self.assertTrue(wizard)
        self.assertEqual(wizard.stock_move_id, move_p1)
        self.assertEqual(wizard.stock_picking_id, move_p1.picking_id)
        tickets_before = self.env["helpdesk.ticket"].search([])
        wizard.description = "Test"
        wizard.create_helpdesk_ticket()
        ticket = self.env["helpdesk.ticket"].search([]) - tickets_before

        self.assertEqual(1, len(ticket))
        self.assertEqual(ticket.team_id, self.purchase_team)
        self.assertEqual(1, self.picking.helpdesk_tickets_count)

        self.assertEqual(1, move_p1.helpdesk_tickets_count)
        self.assertEqual(self.product, ticket.product_id)

    def test_helpdesk_creation_not_allowed(self):
        """
        Create a reception stock picking
        Declare an helpdesk ticket on stock move
        An exception should occur
        """
        self._create_picking()
        move_p1 = self.picking.move_ids.filtered(
            lambda move: move.product_id == self.product
        )
        move_p1.picking_id.picking_type_id.allow_helpdesk_ticket = False
        wizard = (
            self.env["stock.helpdesk.ticket.create"]
            .with_context(active_model="stock.move", active_id=move_p1.id)
            .create({})
        )
        self.assertTrue(wizard)
        self.assertEqual(wizard.stock_move_id, move_p1)
        self.assertEqual(wizard.stock_picking_id, move_p1.picking_id)
        wizard.description = "Test"
        with self.assertRaises(ValidationError):
            wizard.create_helpdesk_ticket()

    def test_actions(self):
        self._create_picking()
        result = self.picking.create_or_show_helpdesk_ticket()
        self.assertEqual(
            result["res_model"],
            "stock.helpdesk.ticket.create",
        )
        move_p1 = self.picking.move_ids.filtered(
            lambda move: move.product_id == self.product
        )
        result = move_p1.create_or_show_helpdesk_ticket()
        self.assertEqual(
            result["res_model"],
            "stock.helpdesk.ticket.create",
        )
        wizard = (
            self.env["stock.helpdesk.ticket.create"]
            .with_context(active_model="stock.move", active_id=move_p1.id)
            .create({})
        )
        wizard.description = "Test"
        wizard.create_helpdesk_ticket()
        action = self.picking.action_view_helpdesk_tickets()
        self.assertEqual(action["domain"], [("stock_picking_id", "=", self.picking.id)])
        result = self.picking.create_or_show_helpdesk_ticket()
        self.assertEqual(
            result["res_model"],
            "helpdesk.ticket",
        )

        result = move_p1.create_or_show_helpdesk_ticket()
        self.assertEqual(
            result["res_model"],
            "helpdesk.ticket",
        )

    def test_domain(self):
        self._create_picking()
        move_p1 = self.picking.move_ids.filtered(
            lambda move: move.product_id == self.product
        )
        wizard = (
            self.env["stock.helpdesk.ticket.create"]
            .with_context(active_model="stock.move", active_id=move_p1.id)
            .create({})
        )
        wizard.description = "Test"
        self.assertEqual(
            wizard.stock_move_id_domain, [("picking_id", "=", move_p1.picking_id.id)]
        )
        wizard.create_helpdesk_ticket()
        ticket = self.env["helpdesk.ticket"].search(
            [("stock_move_id", "=", move_p1.id)]
        )
        self.assertEqual(
            ticket.stock_move_id_domain, [("picking_id", "=", move_p1.picking_id.id)]
        )
