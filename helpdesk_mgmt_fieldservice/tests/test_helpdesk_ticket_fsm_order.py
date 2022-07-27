# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import Form, SavepointCase


class TestHelpdeskTicketFSMOrder(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.helpdesk_ticket = cls.env["helpdesk.ticket"]
        cls.fsm_order = cls.env["fsm.order"]
        cls.partner = cls.env["res.partner"].create({"name": "Partner 1"})
        cls.user_demo = cls.env.ref("base.user_demo")
        cls.helpdesk_ticket_team = cls.env["helpdesk.ticket.team"]
        cls.fsm_team = cls.env["fsm.team"].create({"name": "FSM Team"})
        cls.mail_alias = cls.env["mail.alias"]
        cls.stage_closed = cls.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_done")
        cls.stage_completed = cls.env.ref("fieldservice.fsm_stage_completed")
        cls.test_location = cls.env.ref("fieldservice.test_location")
        cls.partner.service_location_id = cls.test_location
        cls.mail_alias_id = cls.mail_alias.create(
            {
                "alias_name": "Test Mail Alias",
                "alias_model_id": cls.env["ir.model"]
                .search([("model", "=", "helpdesk.ticket")])
                .id,
            }
        )
        cls.team_id = cls.helpdesk_ticket_team.create(
            {"name": "Team 1", "alias_id": cls.mail_alias_id.id}
        )

        cls.ticket_1 = cls.helpdesk_ticket.create(
            {
                "name": "Test 1",
                "description": "Ticket test",
                "user_id": cls.user_demo.id,
                "team_id": cls.team_id.id,
                "fsm_location_id": cls.test_location.id,
            }
        )
        cls.ticket_2 = cls.helpdesk_ticket.create(
            {
                "name": "Test 2",
                "description": "Ticket test",
                "user_id": cls.user_demo.id,
                "team_id": cls.team_id.id,
                "fsm_location_id": cls.test_location.id,
            }
        )
        cls.fsm_order_no_ticket = cls.fsm_order.create(
            {
                "name": "No ticket order",
                "location_id": cls.test_location.id,
                "team_id": cls.fsm_team.id,
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
        fsm_order_obj = self.fsm_order.with_context(**action_create_order["context"])
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
        self.assertFalse(self.ticket_1.all_orders_closed)
        self.assertEqual(self.ticket_1.stage_id.name, self.stage_closed.name)
        self.assertEqual(self.ticket_1.resolution, "Just another resolution")
        # check action_complete on fsm.order no ticket
        self.fsm_order_no_ticket.action_complete()
        self.assertEqual(self.fsm_order_no_ticket.stage_id, self.stage_completed)
        self.assertFalse(self.fsm_order_no_ticket.is_button)
