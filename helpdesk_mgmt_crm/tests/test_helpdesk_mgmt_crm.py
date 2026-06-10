# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import Command
from odoo.tests.common import new_test_user, users

from odoo.addons.base.tests.common import BaseCommon


class TestHelpdeskMgmtCrm(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = new_test_user(
            cls.env,
            login="sale-user",
            groups="helpdesk_mgmt.group_helpdesk_user,sales_team.group_sale_salesman",
        )
        cls.user2 = new_test_user(
            cls.env, login="sale-user2", groups="sales_team.group_sale_salesman"
        )
        cls.team = cls.env["crm.team"].create(
            {"name": "Test team", "member_ids": [Command.set([cls.user2.ids])]}
        )
        cls.team.message_subscribe(
            partner_ids=[cls.user2.partner_id.id],
        )
        cls.ticket = cls.env["helpdesk.ticket"].create(
            {
                "name": "Test ticket",
                "partner_id": cls.user.partner_id.id,
                "user_id": cls.user.id,
                "description": "Test description",
            }
        )

    @users("sale-user")
    def test_action_lead_create(self):
        # Re-browse in sale-user env to avoid admin env context mismatch
        ticket = self.ticket.with_env(self.env)
        team = self.team.with_env(self.env)

        ticket.message_subscribe(
            partner_ids=ticket.partner_id.ids,
            subtype_ids=[self.env.ref("mail.mt_comment").id],
        )
        # pylint: disable=translation-required
        ticket.message_post(body="Ejemplo", subtype_xmlid="mail.mt_comment")
        self.assertIn(
            ticket.partner_id,
            ticket.mapped("message_follower_ids.partner_id"),
        )

        old_ticket_msg_count = len(ticket.message_ids)

        wizard = (
            self.env["helpdesk.ticket.create.lead"]
            .with_context(active_id=ticket.id)
            .create({"team_id": team.id})
        )
        res = wizard.action_helpdesk_ticket_to_lead()
        ticket.invalidate_recordset()

        self.assertTrue(ticket.lead_ids)
        self.assertEqual(res["res_id"], ticket.lead_ids.id)
        self.assertEqual(res["res_model"], ticket.lead_ids._name)
        self.assertEqual(ticket.lead_ids.type, "opportunity")
        self.assertEqual(ticket.name, ticket.lead_ids.name)
        self.assertEqual(ticket.partner_id, ticket.lead_ids.partner_id)
        self.assertEqual(ticket.user_id, ticket.lead_ids.user_id)
        self.assertEqual(ticket.description, ticket.lead_ids.description)

        ticket.lead_ids.invalidate_recordset()
        self.assertGreater(len(ticket.lead_ids.message_ids), 0)
        self.assertGreater(len(ticket.message_ids), old_ticket_msg_count)

        lead_follower_partners = ticket.lead_ids.message_follower_ids.mapped(
            "partner_id"
        )
        self.assertIn(ticket.partner_id, lead_follower_partners)

        res = ticket.action_open_leads()
        self.assertEqual(res["res_model"], ticket.lead_ids._name)
        self.assertEqual(res["res_id"], ticket.lead_ids.id)

    def test_compute_lead_count(self):
        """Test the computation of lead_count field."""
        self.assertEqual(self.ticket.lead_count, 0)

        # Create a lead linked to the ticket
        self.env["crm.lead"].create({"name": "Test Lead", "ticket_id": self.ticket.id})
        self.ticket._compute_lead_count()
        self.assertEqual(self.ticket.lead_count, 1)

        # Create another lead and check count updates
        self.env["crm.lead"].create(
            {"name": "Test Lead 2", "ticket_id": self.ticket.id}
        )
        self.ticket._compute_lead_count()
        self.assertEqual(self.ticket.lead_count, 2)

    def test_action_open_leads_multiple(self):
        """Test action_open_leads when multiple leads exist."""
        lead1 = self.env["crm.lead"].create(
            {"name": "Lead 1", "ticket_id": self.ticket.id}
        )
        lead2 = self.env["crm.lead"].create(
            {"name": "Lead 2", "ticket_id": self.ticket.id}
        )

        action_result = self.ticket.action_open_leads()
        self.assertEqual(action_result["res_model"], "crm.lead")
        self.assertIn("domain", action_result)
        domain_value = next((d for d in action_result["domain"] if d[0] == "id"), None)
        self.assertIsNotNone(domain_value)
        self.assertEqual(domain_value[0], "id")
        self.assertEqual(domain_value[1], "in")
        self.assertCountEqual(domain_value[2], [lead1.id, lead2.id])
