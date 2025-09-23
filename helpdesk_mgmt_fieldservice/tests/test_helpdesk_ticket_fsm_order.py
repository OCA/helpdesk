# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests import Form, TransactionCase
from odoo.tools import html2plaintext

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestHelpdeskTicketFSMOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.partner = cls.env["res.partner"].create({"name": "Partner 1"})
        cls.user_demo = cls.env.ref("base.user_demo")
        cls.fsm_team = cls.env["fsm.team"].create({"name": "FSM Team"})
        cls.fsm_stage_new = cls.env.ref("fieldservice.fsm_stage_new")
        cls.fsm_stage_cancelled = cls.env.ref("fieldservice.fsm_stage_cancelled")
        cls.stage_closed = cls.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_done")
        cls.stage_completed = cls.env.ref("fieldservice.fsm_stage_completed")
        cls.test_location = cls.env.ref("fieldservice.test_location")
        cls.partner.service_location_id = cls.test_location
        cls.mail_alias_id = cls.env["mail.alias"].create(
            {
                "alias_name": "Test Mail Alias",
                "alias_model_id": cls.env["ir.model"]
                .search([("model", "=", "helpdesk.ticket")])
                .id,
            }
        )
        cls.team_id = cls.env["helpdesk.ticket.team"].create(
            {"name": "Team 1", "alias_id": cls.mail_alias_id.id}
        )

        cls.ticket_1 = cls.env["helpdesk.ticket"].create(
            {
                "name": "Test 1",
                "description": "Ticket test",
                "user_id": cls.user_demo.id,
                "team_id": cls.team_id.id,
                "fsm_location_id": cls.test_location.id,
            }
        )
        cls.ticket_2 = cls.env["helpdesk.ticket"].create(
            {
                "name": "Test 2",
                "description": "Ticket test",
                "user_id": cls.user_demo.id,
                "team_id": cls.team_id.id,
                "fsm_location_id": cls.test_location.id,
            }
        )
        cls.fsm_order_no_ticket = cls.env["fsm.order"].create(
            {
                "name": "No ticket order",
                "location_id": cls.test_location.id,
                "team_id": cls.fsm_team.id,
            }
        )
        cls.fsm_stage_closed = cls.env["fsm.stage"].create(
            {
                "name": "Custom Closing Stage",
                "stage_type": "order",
                "is_closed": True,
                "sequence": 200,
            }
        )

    @classmethod
    def _create_ticket_fsm_orders(cls, ticket, number: int = 1):
        action = ticket.action_create_order()
        model = cls.env[action["res_model"]].with_context(**action["context"])
        return model.create([{}] * number)

    def test_helpdesk_ticket_fsm_order(self):
        """
        Checks actions related to the ticket and fieldservice
        """
        # checking action_create_order on fsm.order
        fsm_orders = self._create_ticket_fsm_orders(self.ticket_1, 5)
        self.assertRecordValues(
            fsm_orders,
            [
                {
                    "ticket_id": self.ticket_1.id,
                    "priority": self.ticket_1.priority,
                    "location_id": self.test_location.id,
                    "description": html2plaintext(self.ticket_1.description).strip(),
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
                "search_default_open": 1,
                "default_fsm_location_id": self.test_location.id,
                "default_partner_id": self.test_location.partner_id.id,
            },
        )
        self.ticket_2.fsm_location_id = False
        action_view_ticket = self.test_location.action_view_ticket()
        self.assertEqual(action_view_ticket["views"], [(False, "form")])
        self.assertEqual(action_view_ticket["res_id"], self.ticket_1.id)
        # checking action_complete on fsm.order with ticket
        resolution = "High resolution"
        for idx, order in enumerate(fsm_orders[:-1]):
            order.resolution = resolution + f" {str(idx + 1)}"
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
            action_complete_last_order["res_model"],
            "fsm.order.close.wizard",
        )
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
        with Form(fsm_order_close_wizard) as wizard:
            wizard.stage_id = self.stage_closed
        wizard.record.action_close_ticket()
        self.assertEqual(self.ticket_1.stage_id.name, self.stage_closed.name)
        self.assertEqual(self.ticket_1.resolution, "Just another resolution")
        # check action_complete on fsm.order no ticket
        self.fsm_order_no_ticket.action_complete()
        self.assertEqual(self.fsm_order_no_ticket.stage_id, self.stage_completed)
        self.assertFalse(self.fsm_order_no_ticket.is_button)

    def test_recompute_location_if_partner_with_default_location_is_set(self):
        other_location = self.env.ref("fieldservice.location_1")
        other_partner = other_location.partner_id
        other_partner.service_location_id = other_location
        self.ticket_1.partner_id = other_location.partner_id
        self.assertEqual(self.ticket_1.fsm_location_id, other_location)

    def test_recompute_location_if_commercial_partner_with_default_location_is_set(
        self,
    ):
        other_location = self.env.ref("fieldservice.location_1")
        other_partner = other_location.partner_id
        other_partner.service_location_id = other_location
        other_contact = self.env["res.partner"].create(
            {
                "name": "Other Contact",
                "parent_id": other_partner.id,
            }
        )
        self.ticket_1.partner_id = other_contact
        self.assertEqual(self.ticket_1.fsm_location_id, other_location)

    def test_keep_location_if_partner_without_default_location_is_set(self):
        other_location = self.env.ref("fieldservice.location_1")
        other_partner = other_location.partner_id
        other_partner.service_location_id = False
        self.ticket_1.partner_id = other_location.partner_id
        self.assertEqual(self.ticket_1.fsm_location_id, self.test_location)

    def test_can_close_ticket_if_no_fsm_order(self):
        self.ticket_1.stage_id = self.stage_closed

    def test_can_close_ticket_if_all_fsm_orders_are_closed(self):
        orders = self._create_ticket_fsm_orders(self.ticket_1, 2)
        orders.stage_id = self.fsm_stage_closed
        self.ticket_1.stage_id = self.stage_closed

    def test_can_not_close_ticket_if_none_fsm_order_is_closed(self):
        self._create_ticket_fsm_orders(self.ticket_1, 2)
        with self.assertRaisesRegex(
            ValidationError, "Please complete all service orders"
        ):
            self.ticket_1.stage_id = self.stage_closed

    def test_can_not_close_ticket_if_only_some_fsm_order_are_closed(self):
        orders = self._create_ticket_fsm_orders(self.ticket_1, 2)
        orders[0].stage_id = self.fsm_stage_closed
        with self.assertRaisesRegex(
            ValidationError, "Please complete all service orders"
        ):
            self.ticket_1.stage_id = self.stage_closed
