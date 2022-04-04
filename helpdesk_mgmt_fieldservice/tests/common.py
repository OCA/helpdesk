# Copyright (C) 2022 Trevi Software
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import timedelta

from odoo import fields
from odoo.tests import common


class TestHelpdeskFieldservice(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.Ticket = cls.env["helpdesk.ticket"]
        cls.FSMOrder = cls.env["fsm.order"]

        cls.done_stage = cls.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_done")
        cls.fsm_completed = cls.env.ref("fieldservice.fsm_stage_completed")
        cls.test_location = cls.env.ref("fieldservice.test_location")
        cls.test_partner = cls.env.ref("fieldservice.test_loc_partner")
        cls.ticket = cls.Ticket.create({"name": "Test 1", "description": "Ticket test"})

    def create_order(self, ticket=False):

        dtToday = fields.Datetime.today()
        values = {
            "location_id": self.test_location.id,
            "date_start": dtToday,
            "date_end": dtToday + timedelta(hours=16),
            "request_early": dtToday,
        }
        if ticket is not False:
            values.update({"ticket_id": ticket.id})

        return self.FSMOrder.create(values)
