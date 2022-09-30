# Copyright 2021 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.http import request

from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.base_rest.tests.common import BaseRestCase
from odoo.addons.base_rest_attachment.tests.test_attachment import AttachmentCommonCase
from odoo.addons.component.core import WorkContext
from odoo.addons.extendable.tests.common import ExtendableMixin


class HelpdeskTicketCommonCase(AttachmentCommonCase, BaseRestCase, ExtendableMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        collection = _PseudoCollection("helpdesk.rest.services", cls.env)
        cls.services_env = WorkContext(
            model_name="rest.service.registration",
            collection=collection,
            request=request,
        )
        cls.service = cls.services_env.component(usage="helpdesk_ticket")
        cls.setUpExtendable()

    def setUp(self):
        # AttachmentCommonCase.setUp(self)
        ExtendableMixin.setUp(self)
        super().setUp()

    def generate_ticket_data(self, partner=None):
        data = {
            "description": "My order is late",
            "name": "order num 4",
            "category": {"id": self.ref("helpdesk_mgmt.helpdesk_category_3")},
        }
        if partner:
            data["partner"] = partner
        return data

    def assert_ticket_ok(self, ticket):
        self.assertEqual(len(ticket), 1)
        self.assertEqual(ticket.category_id.name, "Odoo")


class HelpdeskTicketNoaccountCase(HelpdeskTicketCommonCase):
    def test_create_ticket_noaccount(self):
        data = self.generate_ticket_data(
            partner={
                "email": "customer+testststs@example.org",
                "name": "Customer",
            }
        )
        self.service.dispatch("create", params=data)
        ticket = self.env["helpdesk.ticket"].search(
            [("partner_email", "=", "customer+testststs@example.org")]
        )
        self.assert_ticket_ok(ticket)

    #        self.assertEqual(ticket.partner_id.email, ticket.partner_email)

    def test_create_ticket_noaccount_attachment(self):
        data = self.generate_ticket_data(
            partner={
                "email": "customer+testststs@example.org",
                "name": "Customer",
            }
        )
        res = self.service.dispatch("create", params=data)
        self.assertEqual(len(res["attachments"]), 0)
        attachment_res = self.create_attachment(res["id"])
        ticket = self.env["helpdesk.ticket"].search(
            [("partner_email", "=", "customer+testststs@example.org")]
        )
        self.assert_ticket_ok(ticket)
        self.assertEqual(ticket.attachment_ids.id, attachment_res["id"])
        self.assertEqual(ticket.partner_id.email, ticket.partner_email)


class HelpdeskTicketAuthenticatedCase(HelpdeskTicketCommonCase):
    def setUp(self):
        super().setUp()
        env = self.services_env.collection.env
        self.services_env.collection.env = env(
            context=dict(
                env.context,
                authenticated_partner_id=self.env.ref("base.res_partner_1").id,
            )
        )
        self.service = self.services_env.component(usage="helpdesk_ticket")

    def test_create_ticket_account_attachment(self):
        data = self.generate_ticket_data()
        res = self.service.dispatch("create", params=data)
        attachment_res = self.create_attachment(res["id"])
        ticket = self.env["helpdesk.ticket"].search([("id", "=", res["id"])])
        self.assert_ticket_ok(ticket)
        self.assertEqual(ticket.attachment_ids.id, attachment_res["id"])

    def test_ticket_message(self):
        data = self.generate_ticket_data()
        res = self.service.dispatch("create", params=data)
        ticket = self.env["helpdesk.ticket"].search([("id", "=", res["id"])])
        self.assert_ticket_ok(ticket)
        message_data = {"body": "Also here is a picture"}
        self.service.dispatch("message_post", ticket.id, params=message_data)
        self.assertEqual(len(ticket.message_ids), 2)  # There is a technical message
