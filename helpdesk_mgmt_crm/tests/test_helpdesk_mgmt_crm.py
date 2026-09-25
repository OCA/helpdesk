# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from markupsafe import Markup

from odoo.exceptions import AccessError
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
        # Sees every lead, but has no helpdesk access at all.
        cls.user3 = new_test_user(
            cls.env, login="sale-manager", groups="sales_team.group_sale_manager"
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

    @users("sale-user")
    def test_action_lead_create_attachments(self):
        attachment = self.env["ir.attachment"].create(
            {
                "name": "image.png",
                "raw": b"an image",
                "res_model": self.ticket._name,
                "res_id": self.ticket.id,
            }
        )
        self.ticket.message_post(
            body=Markup('<p><img src="/web/image/%s"></p>') % attachment.id,
            attachment_ids=attachment.ids,
            subtype_xmlid="mail.mt_comment",
        )
        wizard = (
            self.env["helpdesk.ticket.create.lead"]
            .with_context(active_id=self.ticket.id)
            .create({"team_id": self.team.id})
        )
        wizard.action_helpdesk_ticket_to_lead()
        lead = self.ticket.lead_ids
        new_message = lead.message_ids.filtered("attachment_ids")
        self.assertEqual(len(new_message), 1)
        new_attachment = new_message.attachment_ids
        self.assertEqual(len(new_attachment), 1)
        # The lead got its own copy, attached to the lead itself.
        self.assertNotEqual(new_attachment, attachment)
        self.assertEqual(new_attachment.res_model, lead._name)
        self.assertEqual(new_attachment.res_id, lead.id)
        self.assertEqual(new_attachment.raw, attachment.raw)
        # The ticket keeps the original.
        self.assertEqual(attachment.res_model, self.ticket._name)
        self.assertEqual(attachment.res_id, self.ticket.id)
        # The inline image in the body points at the copy.
        self.assertIn("/web/image/%s" % new_attachment.id, new_message.body)
        self.assertNotIn("/web/image/%s" % attachment.id, new_message.body)
        # A user who can see the lead but not the ticket can read the copy,
        # which is the whole point: they used to get a placeholder image.
        lead.with_user(self.user3).check_access_rule("read")
        new_attachment.with_user(self.user3).check("read")
        with self.assertRaises(AccessError):
            attachment.with_user(self.user3).check("read")
