# Copyright (C) 2022 Trevi Software
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import Form

from . import common


class TestHelpdeskTicket(common.TestHelpdeskFieldservice):
    def test_close_ticket_with_order(self):

        self.assertFalse(
            self.ticket.all_orders_closed,
            "Initially, field 'all_orders_closed' is False",
        )

        order = self.create_order(ticket=self.ticket)

        with self.assertRaises(ValidationError):
            self.ticket.stage_id = self.done_stage

        order.date_end = fields.Datetime.today()
        order.write({"stage_id": self.fsm_completed.id, "is_button": True})
        self.assertTrue(
            self.ticket.all_orders_closed,
            "After the fsm order is closed 'all_orders_closed' is True",
        )

    def test_set_location_from_partner(self):

        self.assertFalse(
            self.ticket.fsm_location_id,
            "Initially, a service location is not set on the ticket",
        )

        self.test_partner.service_location_id = self.test_location
        with Form(self.ticket) as f:
            f.partner_id = self.test_partner
        self.assertEqual(
            self.ticket.fsm_location_id,
            self.test_location,
            "After a partner is set the corresponding service location is also set",
        )
