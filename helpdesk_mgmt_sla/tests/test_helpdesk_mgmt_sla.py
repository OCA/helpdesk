# Copyright (C) 2020 GARCO Consulting <www.garcoconsulting.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from freezegun import freeze_time

from odoo import fields

from odoo.addons.helpdesk_mgmt_sla.tests.common import CommonHelpdeskMgmtSla


class TestHelpdeskMgmtSla(CommonHelpdeskMgmtSla):
    @freeze_time(fields.Datetime.now() + timedelta(days=7))
    def test_sla_rule_global(self):
        self.env["helpdesk.sla"].check_sla()
        self.assertTrue(self.ticket1.sla_expired)
        self.assertTrue(self.ticket2.sla_expired)

    @freeze_time(fields.Datetime.now() + timedelta(days=7))
    def test_sla_rule_team(self):
        self.sla.team_ids = [(6, 0, [self.team1.id])]
        self.env["helpdesk.sla"].check_sla()
        self.assertTrue(self.ticket1.sla_expired)
        self.assertFalse(self.ticket2.sla_expired)

    @freeze_time(fields.Datetime.now() + timedelta(days=7))
    def test_sla_rule_stage(self):
        self.sla.stage_ids = [(6, 0, [self.stage1.id])]
        self.ticket1.stage_id = self.stage1
        self.ticket2.stage_id = self.stage2
        self.env["helpdesk.sla"].check_sla()
        self.assertTrue(self.ticket1.sla_expired)
        self.assertFalse(self.ticket2.sla_expired)

    @freeze_time(fields.Datetime.now() + timedelta(days=7))
    def test_sla_rule_category(self):
        self.sla.category_ids = [(6, 0, [self.category1.id])]
        self.ticket1.category_id = self.category1
        self.ticket2.category_id = self.category2
        self.env["helpdesk.sla"].check_sla()
        self.assertTrue(self.ticket1.sla_expired)
        self.assertFalse(self.ticket2.sla_expired)

    @freeze_time(fields.Datetime.now() + timedelta(days=7))
    def test_sla_rule_tag(self):
        self.sla.tag_ids = [(6, 0, [self.tag1.id])]
        self.ticket1.tag_ids = self.tag1
        self.ticket2.tag_ids = self.tag2
        self.env["helpdesk.sla"].check_sla()
        self.assertTrue(self.ticket1.sla_expired)
        self.assertFalse(self.ticket2.sla_expired)

    @freeze_time(fields.Datetime.now() + timedelta(days=7))
    def test_sla_rule_domain(self):
        self.sla.domain = f"[('id', '=', {self.ticket1.id})]"
        self.env["helpdesk.sla"].check_sla()
        self.assertTrue(self.ticket1.sla_expired)
        self.assertFalse(self.ticket2.sla_expired)
