# Copyright 2021 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import mock

from odoo.addons.base_rest.tests.common import BaseRestCase

from ..services import attachment


class HelpdeskTicketCase(BaseRestCase):
    def setUp(self):
        super().setUp()
        with self.work_on_services(
            partner=None,
        ) as work:
            self.service = work.component(usage="helpdesk.ticket")
            self.attachment_service = work.component(usage="attachment")

    def create_attachment(self):
        attrs = {"get_data.return_value": b"aaa", "content_type": "image/png"}
        httprequest = mock.Mock(**attrs)
        request = mock.MagicMock()
        request.attach_mock(httprequest, "httprequest")
        attachment.request = request
        res = self.attachment_service.create()
        return res

    def generate_ticket_data(self, partner=None, with_attachment=True):
        if with_attachment:
            self.attachments = self.create_attachment()
        data = {
            "description": "My order is late",
            "name": "order num 4",
            "category": {"id": 3},
        }
        if with_attachment:
            data["attachments"] = [{"id": self.attachments[0].get("id")}]
        if partner:
            data["partner"] = partner
        return data

    def assert_ticket_ok(self, ticket, with_attachment=True):
        self.assertEqual(len(ticket), 1)
        self.assertEqual(ticket.category_id.name, "Odoo")
        if with_attachment:
            self.assertEqual(ticket.attachment_ids.id, self.attachments[0].get("id"))

    def test_create_ticket_noaccount(self):
        data = self.generate_ticket_data(
            partner={
                "email": "customer@example.org",
                "name": "Customer",
            },
            with_attachment=False,
        )
        self.service.dispatch("create", params=data)
        ticket = self.env["helpdesk.ticket"].search(
            [("partner_email", "=", "customer@example.org")]
        )
        self.assert_ticket_ok(ticket, with_attachment=False)
        self.assertEqual(ticket.partner_id.email, ticket.partner_email)

    def test_create_ticket_noaccount_attachment(self):
        data = self.generate_ticket_data(
            partner={
                "email": "customer@example.org",
                "name": "Customer",
            }
        )
        self.service.dispatch("create", params=data)
        ticket = self.env["helpdesk.ticket"].search(
            [("partner_email", "=", "customer@example.org")]
        )
        self.assert_ticket_ok(ticket)
        self.assertEqual(ticket.partner_id.email, ticket.partner_email)

    def test_create_ticket_account_attachment(self):
        self.partner = self.env.ref("base.res_partner_1")
        with self.work_on_services(
            partner=self.partner,
        ) as work:
            self.service = work.component(usage="helpdesk.ticket")
            self.attachment_service = work.component(usage="attachment")

        data = self.generate_ticket_data()
        self.service.dispatch("create", params=data)
        ticket = self.env["helpdesk.ticket"].search(
            [("partner_id", "=", self.partner.id)]
        )
        self.assert_ticket_ok(ticket)

    def test_ticket_message(self):
        self.partner = self.env.ref("base.res_partner_1")
        with self.work_on_services(
            partner=self.partner,
        ) as work:
            self.service = work.component(usage="helpdesk.ticket")
            self.attachment_service = work.component(usage="attachment")

        data = self.generate_ticket_data(with_attachment=False)
        self.service.dispatch("create", params=data)
        ticket = self.env["helpdesk.ticket"].search(
            [("partner_id", "=", self.partner.id)]
        )
        self.assert_ticket_ok(ticket, with_attachment=False)
        message_data = {"body": "Also here is a picture"}
        self.service.dispatch("send_message", ticket.id, params=message_data)
        self.assertEqual(len(ticket.message_ids), 2)  # There is a technical message
        last_message = ticket.message_ids.sorted(key=lambda m: m.create_date)[0]
        self.assertEqual(len(last_message.attachment_ids), 0)
        attachments = self.create_attachment()
        message_data = {
            "body": "Forgot the attachment !",
            "attachments": [{"id": attachments[0].get("id")}],
        }
        self.service.dispatch("send_message", ticket.id, params=message_data)
        self.assertEqual(len(ticket.message_ids), 3)  # There is a technical message
        last_message = ticket.message_ids.sorted(key=lambda m: m.create_date)[0]
        self.assertEqual(len(last_message.attachment_ids), 1)
