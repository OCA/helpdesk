# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests import common
from odoo.tests.common import new_test_user, users


class TestHelpdeskMgmtCrm(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Mr Odoo"})
        cls.user = new_test_user(
            cls.env,
            login="sale-user",
            groups="helpdesk_mgmt.group_helpdesk_user,sales_team.group_sale_salesman",
        )
        cls.user2 = new_test_user(
            cls.env, login="sale-user2", groups="sales_team.group_sale_salesman"
        )
        cls.team = cls.env["crm.team"].create(
            {"name": "Test team", "member_ids": [(6, 0, [cls.user2.id])]}
        )
        cls.team.message_subscribe(
            partner_ids=[cls.user2.partner_id.id],
        )
        cls.ticket = cls.env["helpdesk.ticket"].create(
            {
                "name": "Test ticket",
                "partner_id": cls.partner.id,
                "user_id": cls.user.id,
                "description": "Test description",
            }
        )

    @users("sale-user")
    def test_action_lead_create(self):
        self.ticket.message_subscribe(
            partner_ids=self.ticket.partner_id.ids,
            subtype_ids=[self.env.ref("mail.mt_comment").id],
        )
        # pylint: disable=translation-required
        self.ticket.message_post(body="Ejemplo", subtype_xmlid="mail.mt_comment")
        self.assertIn(
            self.ticket.partner_id,
            self.ticket.mapped("message_follower_ids.partner_id"),
        )
        old_messages = self.ticket.message_ids
        wizard = (
            self.env["helpdesk.ticket.create.lead"]
            .with_context(active_id=self.ticket.id)
            .create({"team_id": self.team.id})
        )
        res = wizard.action_helpdesk_ticket_to_lead()
        self.assertTrue(self.ticket.lead_ids)
        self.assertEqual(res["res_id"], self.ticket.lead_ids.id)
        self.assertEqual(res["res_model"], self.ticket.lead_ids._name)
        self.assertEqual(self.ticket.lead_ids.type, "opportunity")
        self.assertEqual(self.ticket.name, self.ticket.lead_ids.name)
        self.assertEqual(self.ticket.partner_id, self.ticket.lead_ids.partner_id)
        self.assertEqual(self.ticket.user_id, self.ticket.lead_ids.user_id)
        self.assertEqual(self.ticket.description, self.ticket.lead_ids.description)
        self.assertGreater(len(self.ticket.lead_ids.message_ids), len(old_messages))
        self.assertGreater(len(self.ticket.message_ids), len(old_messages))
        self.assertIn(
            self.user2.partner_id,
            self.ticket.lead_ids.message_follower_ids.mapped("partner_id"),
        )
        self.assertIn(
            self.ticket.partner_id,
            self.ticket.lead_ids.mapped("message_follower_ids.partner_id"),
        )
        # action_open_lead
        res = self.ticket.action_open_leads()
        self.assertEqual(res["res_model"], self.ticket.lead_ids._name)
        self.assertEqual(res["res_id"], self.ticket.lead_ids.id)
