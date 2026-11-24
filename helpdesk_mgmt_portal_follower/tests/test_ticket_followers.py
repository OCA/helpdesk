from odoo import http

from odoo.addons.base.tests.common import HttpCaseWithUserPortal


class TestSubmitPortalTicketBase(HttpCaseWithUserPortal):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.new_ticket_title = "Test title"
        cls.new_ticket_description = ("This is a test",)
        cls.category = cls.env["helpdesk.ticket.category"].create({"name": "test"})
        cls.company = cls.env.ref("base.main_company")

        cls.follower_emails = "test1@testing.com, test2@testing.com"
        cls.partner_model = cls.env["res.partner"]
        cls.helpdesk_ticket_model = cls.env["helpdesk.ticket"]

        cls.partner_portal.parent_id = cls.company.partner_id

    def _submit_ticket_with_followers(self, response_code, **values):
        data = {
            "category": self.category.id,
            "csrf_token": http.Request.csrf_token(self),
            "subject": self.new_ticket_title,
            "description": self.new_ticket_description,
            "followers": self.follower_emails,
        }
        data.update(**values)
        resp = self.url_open("/submitted/ticket", data=data)
        self.assertEqual(resp.status_code, response_code)
        return resp

    def _submit_ticket_without_followers(self, response_code, **values):
        data = {
            "category": self.category.id,
            "csrf_token": http.Request.csrf_token(self),
            "subject": self.new_ticket_title,
            "description": self.new_ticket_description,
            "followers": "",
        }
        data.update(**values)
        resp = self.url_open("/submitted/ticket", data=data)
        self.assertEqual(resp.status_code, response_code)
        return resp


class TestSubmitPortalTicket(TestSubmitPortalTicketBase):
    def test_submit_ticket_with_followers(self):
        self.authenticate("portal", "portal")
        self._submit_ticket_with_followers(response_code=200)

        ticket = self.helpdesk_ticket_model.search(
            [("name", "=", self.new_ticket_title)]
        )

        for email in self.follower_emails.split(","):
            partner = self.partner_model.search([("email", "=", email.strip())])
            self.assertEqual(len(partner), 1)
            self.assertIn(partner.id, ticket.message_partner_ids.ids)

    def test_submit_ticket_without_followers(self):
        self.authenticate("portal", "portal")
        self._submit_ticket_without_followers(response_code=200)

        ticket = self.helpdesk_ticket_model.search(
            [("name", "=", self.new_ticket_title)]
        )

        for email in self.follower_emails.split(","):
            partner = self.partner_model.search([("email", "=", email.strip())])
            self.assertEqual(len(partner), 0)
            self.assertNotIn(partner.id, ticket.message_partner_ids.ids)
