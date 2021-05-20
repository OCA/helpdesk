# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import Form, SavepointCase


class TestHelpdeskTicketFSMOrder(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.HelpdeskTicket = cls.env["helpdesk.ticket"]
        cls.FsmOrder = cls.env["fsm.order"]
        cls.FsmStage = cls.env["fsm.stage"]
        cls.partner = cls.env["res.partner"].create({"name": "Partner 1"})
        cls.user_demo = cls.env.ref("base.user_demo")
        cls.HelpdeskTicketTeam = cls.env["helpdesk.ticket.team"]
        cls.fsm_team = cls.env["fsm.team"].create({"name": "FSM Team"})
        cls.fsm_stage_new = cls.env.ref("fieldservice.fsm_stage_new")
        cls.fsm_stage_cancelled = cls.env.ref("fieldservice.fsm_stage_cancelled")
        cls.MailAlias = cls.env["mail.alias"]
        cls.stage_closed = cls.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_done")
        cls.stage_completed = cls.env.ref("fieldservice.fsm_stage_completed")
        cls.test_location = cls.env.ref("fieldservice.test_location")
        cls.partner.service_location_id = cls.test_location
        cls.mail_alias_id = cls.MailAlias.create(
            {
                "alias_name": "Test Mail Alias",
                "alias_model_id": cls.env["ir.model"]
                .search([("model", "=", "helpdesk.ticket")])
                .id,
            }
        )
        cls.team_id = cls.HelpdeskTicketTeam.create(
            {"name": "Team 1", "alias_id": cls.mail_alias_id.id}
        )

        cls.ticket_1 = cls.HelpdeskTicket.create(
            {
                "name": "Test 1",
                "description": "Ticket test",
                "user_id": cls.user_demo.id,
                "team_id": cls.team_id.id,
                "fsm_location_id": cls.test_location.id,
            }
        )
        cls.ticket_2 = cls.HelpdeskTicket.create(
            {
                "name": "Test 2",
                "description": "Ticket test",
                "user_id": cls.user_demo.id,
                "team_id": cls.team_id.id,
                "fsm_location_id": cls.test_location.id,
            }
        )
        cls.fsm_order_no_ticket = cls.FsmOrder.create(
            {
                "name": "No ticket order",
                "location_id": cls.test_location.id,
                "team_id": cls.fsm_team.id,
            }
        )
        cls.fsm_stage_closed = cls.FsmStage.create(
            {
                "name": "Custom Closing Stage",
                "stage_type": "order",
                "is_closed": True,
                "sequence": 200,
            }
        )

    def _create_fsm_orders(self, fsm_order_obj):
        f = Form(fsm_order_obj)
        fsm_order = f.save()
        return fsm_order

    def test_helpdesk_ticket_fsm_order(self):
        """
        Checks actions related to the ticket and fieldservice
        """
        # checking action_create_order on fsm.order
        action_create_order = self.ticket_1.action_create_order()
        fsm_order_obj = self.FsmOrder.with_context(**action_create_order["context"])
        fsm_orders = [self._create_fsm_orders(fsm_order_obj) for _ in range(5)]
        self.assertRecordValues(
            fsm_orders,
            [
                {
                    "ticket_id": self.ticket_1.id,
                    "priority": self.ticket_1.priority,
                    "location_id": self.test_location.id,
                }
                for _ in range(5)
            ],
        )
        self.assertEqual(self.test_location.ticket_count, 2)
        # checking action_view_ticket on fsm.location
        action_view_ticket = self.test_location.action_view_ticket()
        self.assertEqual(
            action_view_ticket["context"],
            {
                "search_default_is_open": 1,
                "default_fsm_location_id": self.test_location.id,
            },
        )
        self.ticket_2.fsm_location_id = False
        action_view_ticket = self.test_location.action_view_ticket()
        self.assertEqual(
            action_view_ticket["views"],
            [(self.env.ref("helpdesk_mgmt.ticket_view_form").id, "form")],
        )
        self.assertEqual(action_view_ticket["res_id"], self.ticket_1.id)
        # checking action_complete on fsm.order with ticket
        resolution = "High resolution"
        for idx, order in enumerate(fsm_orders[:-1]):
            order.resolution = resolution + " %s" % str(idx + 1)
            order.action_complete()
        self.assertRecordValues(
            fsm_orders[:-1],
            [
                {
                    "stage_id": self.stage_completed.id,
                    "is_button": False,
                }
                for _ in range(4)
            ],
        )
        fsm_orders[-1].resolution = "Just another resolution"
        action_complete_last_order = fsm_orders[-1].action_complete()
        self.assertEqual(
            action_complete_last_order["context"],
            {
                "default_ticket_id": self.ticket_1.id,
                "default_team_id": self.team_id.id,
                "default_resolution": "Just another resolution",
            },
        )
        fsm_order_close_wizard = self.env["fsm.order.close.wizard"].with_context(
            **action_complete_last_order["context"]
        )
        f = Form(fsm_order_close_wizard)
        f.stage_id = self.stage_closed
        close_wizard_form = f.save()
        close_wizard_form.action_close_ticket()
        self.assertTrue(self.ticket_1.all_orders_closed)
        self.assertEqual(self.ticket_1.stage_id.name, self.stage_closed.name)
        self.assertEqual(self.ticket_1.resolution, "Just another resolution")
        # check action_complete on fsm.order no ticket
        self.fsm_order_no_ticket.action_complete()
        self.assertEqual(self.fsm_order_no_ticket.stage_id, self.stage_completed)
        self.assertFalse(self.fsm_order_no_ticket.is_button)

    def test_all_orders_closed(self):
        """
        One of the things this test is for is avoiding hardcoding the name
        of the fsm.stage in the compute method of all_orders_closed
        as was previously done
        """

        self.assertFalse(self.ticket_1.fsm_order_ids)
        self.assertFalse(
            self.ticket_1.all_orders_closed,
            "Helpdesk Ticket: with no linked FSM Order, "
            "all_orders_closed should be False",
        )

        action_create_order = self.ticket_1.action_create_order()
        fsm_order_obj = self.FsmOrder.with_context(**action_create_order["context"])
        fsm_orders = [self._create_fsm_orders(fsm_order_obj) for _ in range(3)]

        self.assertFalse(
            any(order.stage_id.is_closed for order in fsm_orders),
            "FSM Orders should all be open by default",
        )

        self.assertFalse(
            self.ticket_1.all_orders_closed,
            "Helpdesk Ticket: with multiple orders open, "
            "all_orders_closed should be False",
        )

        fsm_orders[0].stage_id = self.fsm_stage_closed
        self.assertFalse(
            self.ticket_1.all_orders_closed,
            "Helpdesk Ticket: only one order closed, "
            "all_orders_closed should still be False",
        )

        fsm_orders[1].ticket_id = False
        self.assertFalse(
            self.ticket_1.all_orders_closed,
            "Helpdesk Ticket: one order closed, one open, one unlinked, "
            "all_orders_closed should still be False",
        )

        fsm_orders[2].stage_id = self.fsm_stage_cancelled
        self.assertTrue(
            self.ticket_1.all_orders_closed,
            "Helpdesk Ticket: one order closed, one cancelled, one unlinked, "
            "all_orders_closed should be True",
        )

        fsm_orders[1].ticket_id = self.ticket_1.id
        self.assertFalse(
            self.ticket_1.all_orders_closed,
            "Helpdesk Ticket: relinking previous order "
            "all_orders_closed should be False",
        )

        fsm_orders[1].stage_id.is_closed = True
        self.assertTrue(
            self.ticket_1.all_orders_closed,
            "Helpdesk Ticket: changed 'is_closed' attribute on order's state"
            "all_orders_closed should be True",
        )
