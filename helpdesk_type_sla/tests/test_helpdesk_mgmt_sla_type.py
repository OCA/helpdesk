# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import timedelta

from freezegun import freeze_time

from odoo import Command, fields

from odoo.addons.helpdesk_mgmt_sla.tests.common import CommonHelpdeskMgmtSla


class TestHelpDeskRule(CommonHelpdeskMgmtSla):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.type1 = cls.env["helpdesk.ticket.type"].create({"name": "Type One"})
        cls.type2 = cls.env["helpdesk.ticket.type"].create({"name": "Type Two"})

    def test_sla_rule_type(self):
        self.sla.type_ids = [Command.set([self.type1.id])]
        ticket1 = self.get_ticket(self.team1, {"type_id": self.type1.id})
        ticket2 = self.get_ticket(self.team2, {"type_id": self.type2.id})
        with freeze_time(fields.Datetime.now() + timedelta(days=7)):
            self.assertTrue(ticket1.sla_expired)
            self.assertFalse(ticket2.sla_expired)

    def test_sla_rule_no_type(self):
        ticket1 = self.get_ticket(self.team1, {"type_id": self.type1.id})
        ticket2 = self.get_ticket(self.team2, {"type_id": self.type2.id})
        with freeze_time(fields.Datetime.now() + timedelta(days=7)):
            self.assertTrue(ticket1.sla_expired)
            self.assertTrue(ticket2.sla_expired)
