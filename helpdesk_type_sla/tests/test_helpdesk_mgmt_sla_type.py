# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

from freezegun import freeze_time

from odoo import fields

from odoo.addons.helpdesk_mgmt_sla.tests.common import CommonHelpdeskMgmtSla


class TestHelpDeskRule(CommonHelpdeskMgmtSla):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.type1 = cls.env["helpdesk.ticket.type"].create({"name": "Type One"})
        cls.type2 = cls.env["helpdesk.ticket.type"].create({"name": "Type Two"})

    @freeze_time(fields.Datetime.now() + timedelta(days=7))
    def test_sla_rule_stage(self):
        self.sla.type_ids = [(6, 0, [self.type1.id])]
        self.ticket1.type_id = self.type1
        self.ticket2.type_id = self.type2
        self.env["helpdesk.sla"].check_sla()
        self.assertTrue(self.ticket1.sla_expired)
        self.assertFalse(self.ticket2.sla_expired)
