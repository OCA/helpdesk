# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestMgmtsystemNonconformity(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.nonconformity_stage_1 = cls.env["mgmtsystem.nonconformity.stage"].create(
            {"name": "Stage 1"}
        )
        cls.nonconformity_stage_2 = cls.nonconformity_stage_1.copy({"name": "Stage 2"})
        cls.nonconformity_stage_3 = cls.nonconformity_stage_2.copy({"name": "Stage 3"})
        cls.ticket_stage_1 = cls.env["helpdesk.ticket.stage"].create(
            {"name": "Stage 1", "nonconformity_stage_id": cls.nonconformity_stage_1.id}
        )
        cls.ticket_stage_2 = cls.ticket_stage_1.copy(
            {"name": "Stage 2", "nonconformity_stage_id": cls.nonconformity_stage_2.id}
        )
        cls.partner = cls.env["res.partner"].create({"name": "Mr Odoo"})

    def test_create_ticket(self):
        ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test ticket",
                "partner_id": self.partner.id,
                "user_id": self.env.ref("base.user_admin").id,
                "description": "description",
                "stage_id": self.ticket_stage_1.id,
            }
        )
        self.assertFalse(ticket.nonconformity_id)
        ticket.action_nonconformity_create()
        self.assertTrue(ticket.nonconformity_id)
        self.assertEqual(ticket.nonconformity_id.stage_id, self.nonconformity_stage_1)
        ticket.stage_id = self.ticket_stage_2
        self.assertEqual(ticket.nonconformity_id.stage_id, self.nonconformity_stage_2)
        ticket.nonconformity_id.stage_id = self.nonconformity_stage_3
        self.assertEqual(ticket.stage_id, self.ticket_stage_2)
        ticket.nonconformity_id.stage_id = self.nonconformity_stage_1
        self.assertEqual(ticket.stage_id, self.ticket_stage_1)
